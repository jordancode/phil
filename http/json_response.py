import datetime
import json
from builtins import Exception
from json.encoder import JSONEncoder

from werkzeug.wrappers import (BaseResponse,ETagResponseMixin,
               CommonResponseDescriptorsMixin,
               WWWAuthenticateMixin)

from framework.utils.date_utils import DateUtils
from app.utils.constants import SERVER_VERSION, MIN_SUPPORTED_CLIENTS
from framework.utils.json_utils import JSONUtils


class JSONResponse(BaseResponse,ETagResponseMixin,
               CommonResponseDescriptorsMixin,
               WWWAuthenticateMixin):
    
    """
        HTML response for the JSON api.
        
        Every response has a few standard keys in it
        "success" : True or False, did it work?
        "now_ts" : server time,
        "v" : current server version,
        "min_v" : required client version
        
    
    """
    
    _success = True
    _user = None
    
    def __init__(self, data_dict=None, headers=None, status=200, optional_keys=None, caller=None, user=None):
        if data_dict is None:
            data_dict = {}
            
        if type(data_dict) is not dict:
            raise BadResponseData(data_dict)
            
        self.set_data_dict(data_dict)
        
        if optional_keys:
            self.set_optional_keys(optional_keys)    
        elif caller is not None and hasattr(caller, "meta") and "optional_keys" in caller.meta:
            self.set_optional_keys(caller.meta["optional_keys"])
        
        
        self._user = user
        
        super().__init__(None, status=status, headers=headers, content_type="text/json")
    
    
    _data_dict = None
    _optional_keys = None
    
    def set_data_dict(self,dict_):
        self._data_dict = dict_
        
        
    def get_data_dict(self):
        return self._data_dict
    
    def set_optional_keys(self, optional_keys):
        self._optional_keys = optional_keys
        
    
    def _add_in_extra_keys(self):
        self._data_dict["success"] = self._success
        self._data_dict["now_ts"] = DateUtils.datetime_to_unix()
        self._data_dict["v"] = SERVER_VERSION
        self._data_dict["min_v"] = MIN_SUPPORTED_CLIENTS
        
    
    def _update_response(self):
        response = None
        
        if self._data_dict is not None:
            response = JSONUtils.dumps(self._data_dict, optional_keys=self._optional_keys, context=self._user)
        
        self.set_data(response)
        
        return response
    
    
    
        
    def set_error(self, error = None, friendly_message = None, status = 400):
        self._success = False
        if error:
            if hasattr(error, "description"):
                self.set_key("description",error.description)
            
            if hasattr(error, "code"):
                self.set_key("code", error.code)
                self.status_code = error.code
            elif self.status_code != status:
                self.status_code = status
                
            self.set_key("error", error)
            
            if friendly_message:
                self.set_key("display_error_message",friendly_message)
            elif hasattr(error, "get_friendly_message"):
                self.set_key("display_error_message",error.get_friendly_message())
        
            
        return self
        

    def set_key(self,key,value):
        """
            Key is a string (sets one level) or an array of strings (recurses data, creates keys if don't exist)
            Value can be any json-allowed type: (string, number, array, dictionary, None) 
        """
        if key is not None:
            if self._data_dict is None:
                self._data_dict = {}
                
            dict = self._data_dict
            
            if isinstance(key, str):
                key_arr = [key]
            else:
                key_arr = key
                
            for index, subkey in enumerate(key_arr):
                if index == len(key_arr) - 1:
                    dict[subkey] = value
                else:
                    if subkey in dict:
                        dict = dict[subkey]
                    else:
                        dict[subkey] = {}
                        
                        
        return self
        
    def get_wsgi_response(self, environ):
        self._add_in_extra_keys()
        self._update_response()
        
        return super().get_wsgi_response(environ)
            
    @property
    def success(self):
        
        return self._success
    
    @success.setter
    def success(self, is_success):
        self._success = is_success
    
    
class CustomEncoder(JSONEncoder):
    
    def encode(self,o):
        try:
            if o > self._MAX_32_BIT_INT:
                return repr(str(o))
        except TypeError as e:
            pass
        
        return super().encode(o)
    
    
        
        
        
class BadResponseData(Exception):
    def __init__(self, data_thing):
        super().__init__("Bad response data: " + str(type(data_thing)))    
    
    