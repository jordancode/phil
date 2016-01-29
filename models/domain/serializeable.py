from abc import ABCMeta
from framework.utils.id import Id

class Serializeable(metaclass=ABCMeta):
    
    @classmethod
    def get_definition(cls):
        #abstract, returns definition config
        return None
    
    @classmethod
    def get_definition_for_keys(cls, optional_keys = None):
        #returns the required definition plus 
        #any optional keys in the "optional_keys" array/dict
        
        defn = cls.get_definition()
        if defn is None:
            return None
        
        key_list = cls._get_optional_keys_for_class(optional_keys)
        key_dict = {key : True for key in key_list}
        
        ret = {}
        for key,attr in defn.items():
            if attr.is_required() or key in key_dict:
                ret[key] = attr
        
        return ret
        
    
    @classmethod
    def get_key_to_type(cls, optional_keys):
        
        return cls._recursive_key_to_type([],optional_keys)
        
        
    @classmethod
    def _get_optional_keys_for_class(cls, optional_keys = None):
        try:
            if isinstance(optional_keys,list):
                return optional_keys
            else:
                return optional_keys[cls.__name__]
            
        except (TypeError, KeyError):
            pass
        
        return []
        
    
    def to_dict(self, stringify_ids = False, optional_keys = None):
        d = self._recursive_to_dict([], stringify_ids, optional_keys)
        
        return d
        
    
    def _recursive_to_dict(self, seen_refs, stringify_ids, optional_keys = None):
        #if we have a circular reference, then simply exit
        if self in seen_refs:
            raise CircularRefException() 
        
        seen_refs.append(self)
        
        state = {
                "object" : self.__class__.__name__
            }
        
        defn = self.get_definition_for_keys(optional_keys)
        
        for key in self._get_keys():
            if not self._include_key(key, defn):
                continue
            
            value = self._get_attr(key)
            try:
                dict = value._recursive_to_dict(seen_refs, stringify_ids, optional_keys)
                state[key] = dict
            except AttributeError:
                new_value = value
                if stringify_ids:
                    new_value = self._stringify_id(value)
                
                state[key] = new_value
            except CircularRefException:
                pass #skip circular references
        
        
        return state
    
    def _include_key(self, key, defn):
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
        defn = self.get_definition() 
        if defn is not None and key in defn:
            if defn[key].is_lazy():
                return defn[key].get_lazy_value(self)
        
        return getattr(self, key)

     
class CircularRefException(Exception):       
    def __init__(self):
        super().__init__("Circular reference while serializing object")