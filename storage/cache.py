import pickle

from memcache import Client
import logging
import json
import pprint


import json
import logging

import memcache
from framework.utils.json_utils import JSONUtils
import json
from framework.config.config import Config


class Cache:

    def __init__(self):

        servers = map(
            lambda c:(c['host'] + ":" + str(c['port']), c['weight']),
            Config.get("memcache", "servers")
        )

        self.mc = memcache.Client(servers, debug=1, pickleProtocol=2)

    _instance = None
    _client = None



    #check if in cache then return value, else None
    def get(self, key):
        key=str(key)

        value = self.mc.get(key)


        logging.getLogger().debug( "qqqqq_GET"+  pprint.pformat(value)  )



        if value is None:
            return None
        
        return value



    #set one key, can use for custom key
    def set(self, key, value):
        if value is None:
            return 


        logging.getLogger().debug( "_SET"+  pprint.pformat(value)  )



        self.mc.set(key, value)


    def expire(self, key):

        self.mc.delete(str(key))


    #check if in cache then return value, else None
    # TAKES [key1, key2]
    # RETURN {'key1' : 'val1', 'key2' : 'val2'}
    def get_multi(self, keys):

        values = self.mc.get_multi(keys)
        if values is None:
            return []

        return values



    # TAKES {'key1' : 'val1', 'key2' : 'val2'}
    def set_multi(self, key_obj):

        self.mc.set_multi(key_obj)
