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

    request_cache_enabled=False
    
    _request_cache = {}
    
    _remote_cache = None
    
    DEFAULT_EXPIRE = 10 * 24 * 3600


    # from request-session memory
    @classmethod
    def _get_from_request_cache(cls, namespace, key):
        if not cls.request_cache_enabled:
            return None
            

        model_name = str(namespace) + str(key)

        if not model_name in cls._request_cache:
            cls._request_cache[model_name] = None

        return cls._request_cache[model_name]


    # from request-session memory
    @classmethod
    def _set_in_request_cache(cls, namespace, key, value):
        if not cls.request_cache_enabled:
            return

        model_name = str(namespace) + str(key)

        cls._request_cache[model_name] = value
    
    
    @classmethod
    def _delete_from_request_cache(cls, namespace, key):
        if not cls.request_cache_enabled:
            return
        
        key = namespace+str(key)
        
        if key in cls._request_cache:
            del cls._request_cache[key]
        

    @classmethod
    def get(cls, namespace, key):

        req_cache = cls._get_from_request_cache( namespace, key)
        if req_cache:
            return req_cache
        else:
            return cls.get_remote_cache().get(namespace+str(key))


    # {namespacekey: val, ..}
    @classmethod
    def set(cls, namespace, key, value, expire=DEFAULT_EXPIRE):
        cls.get_remote_cache().set(namespace+str(key), value, expire)
        cls._set_in_request_cache(namespace, key, value)



    # RETURN {'classnamekey1' : 'val1', 'classnamekey2' : 'val2'}
    @classmethod
    def get_multi(cls, namespace, keys):
        
        ret = {}
        keys_to_fetch = []
        
        for key in keys:
            obj = cls._get_from_request_cache(namespace, key)
            if obj:
                ret[namespace+str(key)] = obj
            else:
                keys_to_fetch.append(key)
        
        cache_res = cls.get_remote_cache().get_multi([namespace+str(key) for key in keys_to_fetch])
        ret.update(cache_res)
        
        return ret


    # modelObj {key: val, ..}
    @classmethod
    def set_multi(cls, namespace, modelObj, expire=DEFAULT_EXPIRE):
        
        for key,model in modelObj.items():
            cls._set_in_request_cache(namespace, namespace+str(key), model)
        
        cls.get_remote_cache().set_multi(modelObj, expire)


    @classmethod
    def delete(cls, namespace, key):
        cls.get_remote_cache().delete(namespace+str(key))
        
        cls._delete_from_request_cache(namespace, key)
    
    @classmethod
    def delete_multi(cls, namespace, keys):
        cls.get_remote_cache().delete_multi( [namespace+str(key) for key in keys] )
        
        for key in keys:
            cls._delete_from_request_cache(namespace, key)
    
    
    @classmethod
    def get_remote_cache(cls):
        if not cls._remote_cache:
            cls._remote_cache = Cache()
        
        return cls._remote_cache
    
    # from request-session memory
    @classmethod
    def clear(cls):
        cls._request_cache.clear()
        _remote_cache=None


