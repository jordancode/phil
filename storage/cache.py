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
from framework.utils.model_cache import ModelCache


class Cache:


    def __init__(self):

        servers = map(
            lambda c:(c['host'] + ":" + str(c['port']), c['weight']),
            Config.get("memcache", "servers")
        )

        self.mc = memcache.Client(servers, debug=1)

    _instance = None
    _client = None



    #check if in cache then return value, else None
    def get(self, key):
        key=str(key)

        #check if in request memory
        # if ModelCache().get_for_model(key):
        #     return ModelCache().get_for_model(key)


        logging.getLogger().debug("CACHE-GET KEY:" + key)

        value = self.mc.get(key)


        logging.getLogger().debug("CACHE-GET VALUE:")
        logging.getLogger().debug(pprint.pformat(value))

        if value is None:
            return None
        
        return value

        #return pickle.loads(value)


    #set one key, can use for custom key
    def set(self, key, value):
        if value is None:
            return 
        
        key=str(key)

        logging.getLogger().debug("CACHE-SET VALUE:")
        logging.getLogger().debug(pprint.pformat(value))

        #value = pickle.dumps(value)

        self.mc.set(key, value)


    def expire(self, key):

        self.mc.delete(key)



    #check if in cache then return value, else None
    def get_multi(self, keys):

        values = self.mc.get_multi(keys)
        if values is None:
            return None

        output=[json.loads(values[i]) for i in values]

        return output


    def set_multi(self, key_obj):
        # {'key1' : 'val1', 'key2' : 'val2'}

        self.mc.set_multi(key_obj)


    def expire_multi(self, keys):

        self.mc.delete_multi(keys)
