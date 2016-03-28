import logging
import pprint

class ModelCache():
    
    _cache = {}
    
    @classmethod
    def get_for_model(cls, model_name):
        if not model_name in cls._cache:
            cls._cache[model_name] = {}
        
        return cls._cache[model_name]
    
    @classmethod
    def clear(cls):
        for class_name, models in cls._cache.items():
            models.clear()
            #logging.getLogger().debug(pprint.pformat(models))
                           
        #weird things happen if the following is uncommented: 
        #can revisit to learn why          
        #cls._cache.clear()
        
        
        
            
    