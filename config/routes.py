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
        
        for subdomain in routes_dict:
            subdomain_routes = routes_dict[subdomain]
            for route in subdomain_routes:
                path = route['route']
                
                #cleanup route data that won't go to Rule
                del route['route']
                try:
                    del route['comment']
                except KeyError:
                    pass
                try:
                    del route['parameters']
                except KeyError:
                    pass
                
                rule = Rule(
                            path,
                            subdomain=subdomain,
                            **route
                            );
                            
                ret.append(rule)
        
        return Map(ret, strict_slashes=False);