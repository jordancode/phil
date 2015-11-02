from werkzeug.routing import Map, Rule
from framework.config.config import Config
from werkzeug.utils import redirect
import copy

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
        
        for subdomain_type in routes_dict:
            subdomain_routes = routes_dict[subdomain_type]
            subdomain = Config.get("app", ["subdomains", subdomain_type])
            
            for route in subdomain_routes:
                path = route['route']
                
                #cleanup route data that won't go to Rul
                
                del route['route']
                
                rule = DocRule(
                            path,
                            subdomain=subdomain,
                            **route
                            );
                            
                ret.append(rule)
        
        return Map(ret, strict_slashes=False);

class DocRule(Rule):
    
    parameters = {}
    comment = None
    
    def __init__(self, *args, comment = None, parameters = None, **kargs):
        super().__init__(*args, **kargs)
        self.parameters = parameters or {}
        self.comment = comment
    
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
    