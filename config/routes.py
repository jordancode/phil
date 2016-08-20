import copy
import importlib
import string

from werkzeug.routing import Map, Rule

from framework.config.config import Config
from framework.utils.type import Type
from framework.config.app_url import AppUrl

BATCH_REQUEST_KEY = "BATCH_REQUEST"

class Routes():
    
    def _get_routes_dict(self):
        """
            needs to return a dictionary in the format:
            
            {
                "subdomain" : [
                    {
                        "route" : "path", 
                        "endpoint" : "controller method"
                        //route info
                    },
                    {
                        "route" : "path", 
                        "endpoint" : "controller method"
                        //route info
                    }
                ]
            }
            
            this can be saved as a config or written inline  
        """
        
        return Config.get("routes")
                
    
    def get_map(self):
        """
            Translates the routes dictionary configuration to a Map object
        """
        routes_dict = copy.deepcopy(self._get_routes_dict())
        ret = []
        
        for host_type in routes_dict:
            routes_for_host = routes_dict[host_type]
            for subdomain in routes_for_host:
                
                subdomain_routes = routes_for_host.get(subdomain)
                host = AppUrl.get(subdomain, host_type, include_protocol=False)
                
                for route in subdomain_routes:
                    path = route['route']
                    
                    #cleanup route data that won't go to Rul
                    
                    del route['route']
                    
                    rule = DocRule(
                                path,
                                host=host,
                                **route
                                )
                                
                    ret.append(rule)
        
        return Map(ret,strict_slashes=False,host_matching=True)

class DocRule(Rule):
    
    parameters = {}
    comment = None
    return_data = None
    not_implemented= False
    
    def __init__(self, *args, comment = None, parameters = None, returns = None, optional_keys=None, **kargs):
        super().__init__(*args, **kargs)
        self.parameters = parameters or {}
        self.comment = comment
        self.return_data =  Type.serialize(returns, optional_keys)
    
    def set_parameters(self, params_dict ):
        self.parameters = params_dict
    
    def set_comment(self, comment ):
        self.comment = comment 
        
    def get_param(self, param_name ):
        for param_data in self.parameters:
            if param_data["name"] == param_name:
                return param_data
        
        return None
    
    def param_listed(self, param_name ):
        return self.get_param(param_name) is not None
         
    def get_param_type(self, param_name ):
        return self.get_param(param_name)['type']
    
    def get_param_required(self, param_name ):
        return self.get_param(param_name)['required']
    
    def get_param_comment(self, param_name ):
        return self.get_param(param_name)['comment']
    
    def get_method(self, request,session_store):
        endpoint = self.endpoint
        
        if endpoint == BATCH_REQUEST_KEY:
            return None
        
        module_name, method = endpoint.rsplit(".",1)
        
        class_name = module_name.split(".")[-1]
        class_name = string.capwords(class_name,"_").replace("_","")

        module = importlib.import_module("app.controllers." + module_name)
        class_ = getattr(module, class_name)
        
        return getattr(class_(request,session_store),method)
    
    def update_rule_with_meta(self, request = None, session_store=None):
        m = self.get_method(request, session_store)
        
        if hasattr(m, "meta"):
            if "comment" in m.meta:
                self.set_comment(m.meta["comment"])
            if "return" in m.meta:
                optional_keys = []
                if "optional_keys" in m.meta:
                    optional_keys = m.meta["optional_keys"]
                self.return_data = Type.serialize(m.meta["return"], optional_keys)
            if "parameters" in m.meta:
                self.set_parameters(m.meta["parameters"])
            if "not_implemented" in m.meta:
                self.not_implemented = True 
            
        return m
    
    def to_dict(self):
        ret = {
                "route" : self.rule,
                "subdomain" : self.subdomain,
                "methods" : [m for m in self.methods if m != "HEAD"],#filter HEAD methods, added automatically
                "endpoint" : self.endpoint,
                "parameters" : self.parameters,
                "comment" : self.comment,
                "return" : self.return_data,
                "not_implemented" : self.not_implemented
            }
        
        if self.comment:
            ret["comment"] = self.comment
        if self.parameters:
            ret["parameters"] = self.parameters
        if self.return_data:
            ret["return"] = self.return_data
        if self.not_implemented:
            ret["not_implemented"] = True
        
        
        return ret