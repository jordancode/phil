from framework.config.config import Config
from framework.config.environment import Environment

class AppUrl:
    
    @staticmethod
    def get( subdomain_type = "web", host_type = "main", include_protocol = True):
        
        config = Config.get("app", ["hosts", host_type]) 
        
        proto = config.get("default_protocol")
        subdomain = config.get("subdomains").get(subdomain_type)
        host = config.get("server_name")
        
        if subdomain is not None:
            if subdomain: 
                full_host =  subdomain + "." + host
            else:
                #handle blank subdomain
                full_host = host
        elif subdomain_type:
            full_host = subdomain_type + "." + host
        else:
            full_host = host
        
        if include_protocol:
            return proto + "://" + full_host
        else:
            return full_host
    
    @classmethod
    def get_current(cls, request, subdomain_type=None, include_protocol=True):
        if not request:
            return cls.get(include_protocol=include_protocol)
        
        if subdomain_type is None:
            subdomain_type=request.get_subdomain()
        
        return cls.get(subdomain_type, request.get_host(), include_protocol)
    
    @classmethod
    def get_email(cls, include_protocol=True):
        if Environment.get() == "PROD":
            return cls.get( "email", "email", include_protocol)
        else:
            return cls.get("email", include_protocol=include_protocol)
    
    
    @classmethod
    def get_current_cookie_domain(cls, request):
        return "." + cls.get_current(include_protocol=False)
        