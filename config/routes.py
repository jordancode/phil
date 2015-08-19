from werkzeug.routing import Map, Rule
from framework.config.config import Config

class Routes():
    
    def _get_routes_dict(self):
        """
            needs to return a dictionary in the format:
            
            {
                "subdomain" : {
                    "path" : {
                                //route info
                            },
                    "path" : {
                                //route info
                            }
                    }
            }
            
            this can be saved as a config or written inline  
        """
        
        return Config.get("routes")
                
    
    def get_map(self):
        """
            Translates the routes dictionary configuration to a Map object
        """
        routes_dict = self._get_routes_dict()
        
        ret = []
        
        for subdomain in routes_dict:
            subdomain_routes = routes_dict[subdomain];
            for path in subdomain_routes:
                route = subdomain_routes[path]
                
                rule = Rule(
                            path,
                            subdomain=subdomain,
                            **route
                            );
                            
                ret.append(rule)
        
        return Map(ret);