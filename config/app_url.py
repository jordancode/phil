from framework.config.config import Config
class AppUrl:
    
    @staticmethod
    def get( subdomain_type = "web", host_type = "main", include_protocol = True):
        
        config = Config.get("app", ["hosts", host_type]) 
        
        proto = config.get("default_protocol")
        subdomain = config.get("subdomains").get(subdomain_type)
        host = config.get("server_name")
        
        if subdomain:
            full_host =  subdomain + "." + host
        elif subdomain_type:
            full_host = subdomain_type + "." + host
        else:
            full_host = host
        
        if include_protocol:
            return proto + "://" + full_host
        else:
            return full_host
        