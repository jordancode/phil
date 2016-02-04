import json
from werkzeug.wrappers import (BaseResponse,ETagResponseMixin,
               CommonResponseDescriptorsMixin,
               WWWAuthenticateMixin)
from builtins import Exception
import pprint
import sys
import logging
from json.encoder import JSONEncoder
import datetime
from framework.utils.type import Type

class JSONResponse(BaseResponse,ETagResponseMixin,
               CommonResponseDescriptorsMixin,
               WWWAuthenticateMixin):
    
    
    _success = True
    
    def __init__(self, data_dict=None, headers=None, status=200, optional_keys=None, caller=None):
        if data_dict is None:
            data_dict = {}
            
        if type(data_dict) is not dict:
            raise BadResponseData(data_dict)
            
        self.set_data_dict(data_dict)
        
        if optional_keys:
            self.set_optional_keys(optional_keys)    
        elif caller is not None and hasattr(caller, "meta") and "optional_keys" in caller.meta:
            self.set_optional_keys(caller.meta["optional_keys"])
        
        
        super().__init__(None, status=status, headers=headers, content_type="text/json")
    
    
    _data_dict = None
    _optional_keys = None
    
    def set_data_dict(self,dict_):
        self._data_dict = dict_
        
        
    def get_data_dict(self):
        return self._data_dict
    
    def set_optional_keys(self, optional_keys):
        self._optional_keys = optional_keys
    
    def _update_response(self):
        response = None
        
        self._data_dict["success"] = self._success
        
        if self._data_dict is not None:
            response = json.dumps(self._data_dict, sort_keys=True, default=self._json_helper)
        
        self.set_data(response)
    
    
    def _json_helper(self, value):
        
        #stringifies otherwise non-json nodes
        try:
            return value.to_dict(True, self._optional_keys)
        except AttributeError:
            pass
        
        try:
            return str(value)
        except AttributeError:
            pass
        
        raise TypeError()
      
        
    def set_error(self, error = None):
        self._success = False
        if error:
            if hasattr(error, "description"):
                self.set_key("description",error.description)
            
            if hasattr(error, "code"):
                self.set_key("code", error.code)
                self.status_code = error.code
                
            self.set_key("error", str(error))
            
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
        self._update_response()
        
        return super().get_wsgi_response(environ)
            
    @property
    def success(self):
        
        return self._success
    
    
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
    
    