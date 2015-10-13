from werkzeug.wrappers import Request
from werkzeug.exceptions import BadRequest, HTTPException
import logging
import pprint

class MethodOverrideRequest(Request):
    
    KEY = "_method"
    
    VALID_METHODS = [
                     "GET",
                     "POST",
                     "PUT",
                     "DELETE",
                     "HEAD",
                     ]
    
    UNSUPPORTED_METHODS = [
                           "TRACE",
                           "CONNECT",
                           "OPTIONS"
                           ]
    
    
    @property
    def method(self):
        ret = super().method
        
        if self.KEY in self.values:
            ret = self.values[self.KEY]
            ret.capitalize()
     
            if ret in self.UNSUPPORTED_METHODS:
                raise UnsuportedHTTPMethodError()
            if ret not in self.VALID_METHODS:
                raise InvalidHTTPMethodError()
        
        return ret
    
    def get_value(self, key, default_value = None, required=False):     
        """
            gets a form or query argument from the "values" array
        """
        return self._get_http_parameter(self.values,key,default_value, required)
    
    def get_query_value(self, key, default_value = None, required = False):
        """
            gets a query (GET) argument from the "args" array
        """
        return self._get_http_parameter(self.args,key,default_value, required) 
    
    def get_form_value(self, key, default_value = None, required = False):
        """
            gets a form (POST) argument from the "form" array
        """
        return self._get_http_parameter(self.form,key,default_value, required)


    def _get_http_parameter(self, dictionary, key, default_value, required):
        try:
            return dictionary[key]
        except KeyError:
            if not required:
                return default_value
            else:
                raise MissingParameterException(key)
      

class MissingParameterException(BadRequest):
    def __init__(self, param_name):
        super().__init__("Parameter " + param_name + " is required")    
    
class UnsuportedHTTPMethodError(BadRequest):
    def __init__(self, value):
        super().__init__(value + " is not a supported HTTP method")    
    
    
class InvalidHTTPMethodError(HTTPException):
    def __init__(self, value):
        super().__init__(value + " is not a valid HTTP method")