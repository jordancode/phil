from werkzeug.wrappers import Request
from werkzeug.exceptions import BadRequest, HTTPException
import logging
import pprint
from framework.http.json_http_exception import JSONHTTPException

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


class MethodOverrideRequest(Request):
    
    def __init__(self, environ, populate_request = True, shallow=False):
        super().__init__(environ, populate_request, shallow)
        self._override_method(environ)
        
    
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
                raise JSONHTTPException(MissingParameterException(key))
     
    def _override_method(self, environ):
        method = self.get_value(KEY,environ['REQUEST_METHOD'])
        method.capitalize()
                  
        if method in UNSUPPORTED_METHODS:
            raise JSONHTTPException(UnsuportedHTTPMethodError)
        if method not in VALID_METHODS:
            raise JSONHTTPException(InvalidHTTPMethodError)
        
        environ['REQUEST_METHOD'] = method 

class MissingParameterException(BadRequest):
    def __init__(self, param_name):
        super().__init__("Parameter " + param_name + " is required")    
    
class UnsuportedHTTPMethodError(BadRequest):
    def __init__(self, value):
        super().__init__(value + " is not a supported HTTP method")    
    
    
class InvalidHTTPMethodError(HTTPException):
    def __init__(self, value):
        super().__init__(value + " is not a valid HTTP method")
        
        
    
    
    
    