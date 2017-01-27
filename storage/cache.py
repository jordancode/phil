from memcache import Client

from framework.config.config import Config


class Cache(Client):
    
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
