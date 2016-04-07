from framework.config.config import Config
class AppUrl:
    
    @staticmethod
    def get(subdomain_type = None):
        if subdomain_type is None:
            subdomain_type = "web"
        
        proto = Config.get("app", "default_protocol")
        subdomain = Config.get("app", ["subdomains", subdomain_type])
        host = Config.get("app", "server_name")
        
        return proto + "://" + subdomain + "." + host
        