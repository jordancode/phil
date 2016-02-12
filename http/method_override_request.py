from werkzeug.wrappers import Request
from werkzeug.exceptions import BadRequest, HTTPException
import logging
import pprint
from framework.http.json_http_exception import JSONHTTPException
import json
from framework.utils.date_utils import DateUtils
from logging import getLogger
from werkzeug.utils import cached_property
from werkzeug.datastructures import MultiDict, CombinedMultiDict

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
    
    def get_json_value(self, key, default_value = None, required = False):
        """
            gets a form (POST) argument from the "form" array
        """
        return self._get_http_parameter(self.json,key,default_value)
    
    
    def get_form_value(self, key, default_value = None, required = False):
        """
            gets a form (POST) argument from the "form" array
        """
        return self._get_http_parameter(self.form,key,default_value)
    
    
    def get_all_values(self):
        if not self.rule or not self.rule.parameters:
            raise NoParametersConfigured()
        
        params = self.rule.parameters
        
        param_values = []
        for p in params:
            n = p["name"]
            if n in self.values:
                param_values.append(self.values[n])
            else:
                param_values.append(None)
                 
        return tuple( v for v in param_values )
    
    @cached_property
    def values(self):
        args = []
        for d in self.args, self.form, self.json:
            if not isinstance(d, MultiDict):
                d = MultiDict(d)
            args.append(d)
        return CombinedMultiDict(args)
    
    @cached_property
    def json(self):
        #returns json form the request body
        data_dict = {}
        try:
            data_str = self.get_data()
            if data_str:
                data_dict = json.loads(data_str.decode("utf-8"))
        except Exception as e:
            return e
        
        return data_dict 

    def _get_http_parameter(self, dictionary, key, default_value):
        required = False
        type = None
        
        if self.rule:
            if self.rule.param_listed(key):
                required = self.rule.get_param_required(key)
                type = self.rule.get_param_type(key)
            else:
                #can throw error in future
                pass
        
        try:
            if self._is_array_type(type):
                base = self._get_base_type(type)
                return self._get_list_param(dictionary,key,base) 
                        
            if self._is_dict_type(type):
                base = self._get_base_type(type)
                return self._get_dict_param(dictionary,key,base)
            else:
                return self._coerce_type(dictionary[key], type)
        except KeyError:
            if not required:
                return default_value
            else:
                raise JSONHTTPException(MissingParameterException(key))
        except (TypeError, ValueError) as e:
            #raise e
            raise JSONHTTPException(BadParameterException(key))
    
    
    def _get_list_param(self, dictionary, key, base_type):
        if key in dictionary:
            ret = list(json.loads(dictionary[key]))
        else:
            ret = dictionary.getlist(key + "[]")
        
        ret = [self._coerce_type(a, base_type) for a in ret]
        
        return ret
    
    def _get_dict_param(self, dictionary, key, base_type):
        if key in dictionary:
            return dict(json.loads(dictionary[key]))
        
        return self._construct_dict(key)
    
    def _construct_dict(self, dictionary, key, base_type):
        ret = {};
        
        prefix = key + "[";
        default_index = 0;
        for d_key, d_value in dictionary.items():
            if d_key.startswith(prefix):
                index = d_key[len(prefix):-1]
                
                if index == "":
                    index = default_index
                    default_index+=1
                
                ret[index] = self._coerce_type(d_value,base_type)
        
        return ret
    
    
    def _coerce_type(self, value, type):
        truthy_values = ["true", "True", "1", 1, True]
        
        if value is not None:
            if type == "int":
                return int(value)
            elif type == "float":
                return float(value)
            elif type == "string":
                return str(value)
            elif type == "bool":
                return value in truthy_values
            elif type == "unixtime":
                #cast to float from string then to int to remove decimal 
                return DateUtils.unix_to_datetime(int(float(value)))
            elif type == "json":
                return json.loads(value)
        
        #unknown type
        return value
    
    def _get_base_type(self, type):
        return type[0:-2]
    
    def _is_array_type(self, type):
        if type is None:
            return False
        
        return type[-2:] == "[]"
    
    def _is_dict_type(self, type):
        if type is None:
            return False
        
        return type[-2:] == "{}"
    
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
        

class NoParametersConfigured(BadRequest):
    def __init__(self):
        super().__init__("No Parameters Configured")
    
    
    
    