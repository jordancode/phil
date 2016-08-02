import logging
import json
import pprint


import json
import logging

import memcache
# from framework.utils.json_utils import JSONUtils
import json
from framework.config.config import Config
from framework.storage.cache import Cache


class ModelCache(Cache):


    _request_cache = {}
    DEFAULT_EXPIRE = 10 * 24 * 3600


    # from request-session memory
    @classmethod
    def get_for_model(cls, namespace, key):

        model_name = str(namespace) + str(key)

        if not model_name in cls._request_cache:
            cls._request_cache[model_name] = False

        return cls._request_cache[model_name]


    # from request-session memory
    @classmethod
    def set_for_model(cls, namespace, key, value):

        model_name = str(namespace) + str(key)

        cls._request_cache[model_name] = value


    @classmethod
    def get(cls, namespace, key):

        req_cache = 0 #cls.get_for_model( namespace, key)
        if req_cache:
            return req_cache
        else:
            return Cache().get(namespace+str(key))


    # {namespacekey: val, ..}
    @classmethod
    def set(cls, namespace, key, value, expire=DEFAULT_EXPIRE):
        Cache().set(namespace+str(key), value, expire)
        cls.set_for_model(namespace, key, value)



    # RETURN {'classnamekey1' : 'val1', 'classnamekey2' : 'val2'}
    @classmethod
    def get_multi(cls, namespace, keys):
        keys = [namespace+str(key) for key in keys]
        return Cache().get_multi(keys)


    # {namespacekey: val, ..}
    @classmethod
    def set_multi(cls, modelObj, expire=DEFAULT_EXPIRE):
        Cache().set_multi(modelObj, expire)


    @classmethod
    def expire(cls, namespace, id):
        Cache().expire(namespace+str(id))
        # del cls._request_cache[model_name]


    # from request-session memory
    @classmethod
    def clear(cls):
        for class_name, models in cls._request_cache.items():
            models.clear()


