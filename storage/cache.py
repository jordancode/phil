import memcache
from framework.config.config import Config


class Cache:

    def __init__(self):

        servers = map(
            lambda c:(c['host'] + ":" + str(c['port']), c['weight']),
            Config.get("memcache", "servers")
        )

        self._client = memcache.Client(servers, debug=1)

    _client = None



    #check if in cache then return value, else None
    def get(self, key):
        key=str(key)
        value = self._client.get(key)

        if value is None:
            return None
        
        return value



    #set one key, can use for custom key
    def set(self, key, value, expire=0):
        if value is None:
            return
        
        self._client.set(key, value, time=expire)


    def delete(self, key):

        self._client.delete(str(key))
    
    
    def delete_multi(self, key_list):
        if len(key_list):

            self._client.delete_multi([str(key) for key in key_list])

    #check if in cache then return value, else None
    # TAKES [key1, key2]
    # RETURN {'key1' : 'val1', 'key2' : 'val2'}
    def get_multi(self, key_list):
        if not len(key_list):
            return {}

        values = self._client.get_multi(key_list)
        if values is None:
            return {}

        return values



    # TAKES {'key1' : 'val1', 'key2' : 'val2'}
    def set_multi(self, key_obj, expire=0):
        if not key_obj:
            return

        self._client.set_multi(key_obj, time=expire)
