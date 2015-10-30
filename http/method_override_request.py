from werkzeug.wrappers import Request
from werkzeug.exceptions import BadRequest, HTTPException
import logging
import pprint
from framework.http.json_http_exception import JSONHTTPException
import json
from framework.utils.date_utils import DateUtils

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
    
    rule = None
    
    def __init__(self, environ, populate_request = True, shallow=False):
        super().__init__(environ, populate_request, shallow)
        self._override_method(environ)
        
    
    def get_value(self, key, default_value = None, required=False):     
        """
            gets a form or query argument from the "values" array
        """
        return self._get_http_parameter(self.values,key,default_value)
    
    def get_query_value(self, key, default_value = None, required = False):
        """
            gets a query (GET) argument from the "args" array
        """
        return self._get_http_parameter(self.args,key,default_value) 
    
    def get_form_value(self, key, default_value = None, required = False):
        """
            gets a form (POST) argument from the "form" array
        """
        return self._get_http_parameter(self.form,key,default_value)


    def _get_http_parameter(self, dictionary, key, default_value):
        required = False
        
        if self.rule:
            if self.rule.param_listed(key):
                required = self.rule.get_param_required(key)
                type = self.rule.get_param_type(key)
            else:
                #can throw error in future
                pass
        
        
        try:
            return self._coerce_type(dictionary[key], type)
        except KeyError:
            if not required:
                return default_value
            else:
                raise JSONHTTPException(MissingParameterException(key))
        except (TypeError, ValueError):
            raise JSONHTTPException(BadParameterException(key))
    
    def _coerce_type(self, value, type):
        if value is not None:
            if type == "int":
                return int(value)
            elif type == "float":
                return float(value)
            elif type == "string":
                return str(value)
            elif type == "bool":
                return bool(value)
            elif type == "unix timestamp":
                return DateUtils.unix_to_datetime(value)
            elif type == "JSON array":
                return list(json.loads(value))
            elif type == "JSON dict":
                return dict(json.loads(value))
        
        
        
        #unknown type
        return value
    
    def _override_method(self, environ):
        
        method = environ['REQUEST_METHOD']
        if KEY in self.values:
            method = self.values[KEY]
             
        method.capitalize()
                  
        if method in UNSUPPORTED_METHODS:
            raise JSONHTTPException(UnsuportedHTTPMethodError)
        if method not in VALID_METHODS:
            raise JSONHTTPException(InvalidHTTPMethodError)
        
        environ['REQUEST_METHOD'] = method 

class BadParameterException(BadRequest):
    def __init__(self, param_name):
        super().__init__("Parameter " + param_name + " is in an unexpected format")

class MissingParameterException(BadRequest):
    def __init__(self, param_name):
        super().__init__("Parameter " + param_name + " is required")    
    
class UnsuportedHTTPMethodError(BadRequest):
    def __init__(self, value):
        super().__init__(value + " is not a supported HTTP method")    
    
    
class InvalidHTTPMethodError(HTTPException):
    def __init__(self, value):
        super().__init__(value + " is not a valid HTTP method")
        
        
    
    
    
    