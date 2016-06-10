import logging
import json
import pprint


import json
import logging

import memcache
from framework.utils.json_utils import JSONUtils
import json
from framework.config.config import Config


class ModelCache():

    
    _request_cache = {}

    # from request memory
    @classmethod
    def get_for_model(cls, model_name):
        if not model_name in cls._request_cache:
            cls._request_cache[model_name] = {}
        
        return cls._request_cache[model_name]

        # from request memory
    @classmethod
    def clear(cls):
        for class_name, models in cls._request_cache.items():
            models.clear()
        

