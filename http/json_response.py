import json
from werkzeug.wrappers import (BaseResponse,ETagResponseMixin,
               CommonResponseDescriptorsMixin,
               WWWAuthenticateMixin)

class JSONResponse(BaseResponse,ETagResponseMixin,
               CommonResponseDescriptorsMixin,
               WWWAuthenticateMixin):
    
    def __init__(self, data_dict=None, headers=None):
        
        self.set_data_dict(data_dict)
        
        super().__init__(None, status=200, headers=headers, content_type="text/json")
    
    
    _data_dict = None
    
    def set_data_dict(self,dict):
        self._data_dict = dict
        
        
    def get_data_dict(self):
        return self._data_dict
    
    
    def _update_response(self):
        response = None
        if self._data_dict is not None:
            response = json.dumps(self._data_dict, sort_keys=True)
        
        self.set_data(response)
    


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
                        
                        
    
    def get_wsgi_response(self, environ):
        self._update_response()
        
        return super().get_wsgi_response(environ)
            
    
        
        
        
    
    