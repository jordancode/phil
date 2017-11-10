from framework.http.method_override_request import MethodOverrideRequest
from framework.config.routes import DocRule
import copy
import werkzeug
import logging
import pprint
from framework.config.config import Config

class BatchRequest(MethodOverrideRequest):
    """
        This will handle an array of requests in one API call
        The requests get exectued in the order that they are received.
        An array of response is returned to the user 
        
    """
    
    def __init__(self, environ, routes):
        super().__init__(environ)
        
        self._init_rule()
        self._routes = routes
    
    def _init_rule(self):
        
        parameters = [
            {
                "name" : "batch",
                "type" : "[]",
                "required" : True
            } 
        ]
        
        self.rule = DocRule("/batch", parameters=parameters)
        
        
        
    def get_sub_requests(self):
        
        request_array = self.get_value("batch")
        host = werkzeug.wsgi.get_host(self.environ)
        
        ret = []
        
        for request_args in request_array:
            
            request = MethodOverrideRequest(self.environ, populate_request=False, shallow=True)
            request.__dict__["form"] = request_args.get("args",request.parameter_storage_class())
            
            adapter = self._routes.bind(host,
                                path_info=request_args.get("path"),
                                default_method=request_args.get("method")
                            )
            
            ret.append( ( request, adapter ) )
        
        
        return ret
    
    