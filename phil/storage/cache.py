from memcache import Client
from framework.config.config import Config

class Cache:
    
    _instance = None
    _client = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            servers = []
            servers = map(
                  lambda c:(c['host'] + ":" + str(c['port']), c['weight']),
                  Config.get("memcache", "servers")
              )
            
            cls._instance = cls(servers)
            
        return cls._instance
    
    def __init__(self, servers, args = None):
        
        if args is not None:
            self._client = Client(servers, **args)
        else:
            self._client = Client(servers)
            
    
    def get(self, key):
        return False
    
    def set(self,key,value, expire = None):
        return None
    
    def expire(self,key, expire):
        return False