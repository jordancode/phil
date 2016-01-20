from abc import ABCMeta
from framework.utils.id import Id

class Serializeable(metaclass=ABCMeta):
    
    def get_definition(self, optional_keys = None):
        return None
    
    def to_dict(self, stringify_ids = False, optional_keys = None):
        d = self._recursive_to_dict([], stringify_ids, optional_keys)
        d["object"] = self.__class__.__name__
        
        return d
        
    
    def _recursive_to_dict(self, seen_refs, stringify_ids, optional_keys = None):
        #if we have a circular reference, then simply exit
        if self in seen_refs:
            raise CircularRefException() 
        
        seen_refs.append(self)
        
        state = {}
        for key in self._get_keys():
            if not self._include_key(key, optional_keys):
                continue
            
            value = self._get_attr(key)
            try:
                dict = value._recursive_to_dict(seen_refs, stringify_ids)
                state[key] = dict
            except AttributeError:
                new_value = value
                if stringify_ids:
                    new_value = self._stringify_id(value)
                
                state[key] = new_value
            except CircularRefException:
                pass #skip circular references
            
        return state
    
    
    def _include_key(self, key, optional_keys_to_include):
        defn = self.get_definition(optional_keys_to_include)
        
        if defn is None:
            return True
        return key in defn
      
     
    def _stringify_id(self, value):
        try:
            if value > Id.MAX_32_BIT_INT:
                return str(value)
        except (TypeError, AttributeError) as e:
            pass
        
        return value
    
    
    def _get_keys(self):
        if self.get_definition() is not None:
            return self.get_definition.keys()
        return []
    
    
    def _get_attr(self, key):
        return getattr(self, key)

     
class CircularRefException(Exception):       
    def __init__(self):
        super().__init__("Circular reference while serializing object")