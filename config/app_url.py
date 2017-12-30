from framework.config.config import Config
from framework.config.environment import Environment

class AppUrl:
    
    @classmethod
    def get(cls, subdomain_type = "web", host_type = "main", include_protocol = True):
        
        config = Config.get("app", ["hosts", host_type]) 
        host = config.get("server_name")
        
        alias_config=cls._get_alias_config(config)
        
        proto = alias_config.get("default_protocol")
        subdomain = alias_config.get("subdomains").get(subdomain_type)
        
        
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
    def get_current_host_type(cls, request):
        domain=cls.get_current(request, "", True)
        host_list = Config.get("app", ["hosts"])
        for host_type, host in host_list.items():
            
            if host['server_name'] == domain:
                return host_type
        
        return None
    
    @classmethod
    def get_email(cls, include_protocol=True):
        if Environment.get() == "PROD":
            return cls.get( "email", "email", include_protocol)
        else:
            return cls.get("email", include_protocol=include_protocol)
    
    
    @classmethod
    def get_current_cookie_domain(cls, request):
        return "." + cls.get_current(request,subdomain_type="",include_protocol=False)
    
    
    @classmethod
    def _get_alias_config(cls, config):
        if config.get("host_alias"):
            return Config.get("app", ["hosts", config['host_alias']])
        else:
            return config