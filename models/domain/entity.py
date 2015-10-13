import copy

class Entity:
    
    #this is the state when fetched from the DAO
    _stored_state = None
    #this is the state after domain modifications
    _current_state = None
    
    _deleted = False
    
    def __init__(self,id):
        #should override with required arguments
        #to satisfy all invariants
        #all domain objects must have an id
        self._stored_state = {}
        self._current_state = {}
        self._set_attr("id",id)
    
    @property
    def id(self):
        return self._get_attr("id")   
    
    @property
    def is_new(self):
        return not self._stored_state
    
    @property
    def is_dirty(self):
        dirty_keys = self.get_dirty_keys()
        
        return not not dirty_keys
    
    @property
    def deleted(self):
        return self._deleted
    
    def set_deleted(self):
        self._deleted = True
    
    def is_key_dirty(self, key):
        dirty_keys = self.get_dirty_keys()
        
        return key in dirty_keys
        
    def get_dirty_keys(self):
        dirty_keys = {}
        for key in set().union(self._stored_state.keys(), self._current_state.keys()):
            current_val = self._get_attr(key)
            if not key in self._stored_state or self._stored_state[key] != current_val:
                dirty_keys[key] = current_val
        
        return dirty_keys                
    
    def to_dict(self):
        return self._recursive_to_dict([])
        
    
    def _recursive_to_dict(self, seen_refs):
        #if we have a circular reference, then simply exit
        if self in seen_refs:
            raise CircularRefException() 
        
        seen_refs.append(self)
        
        state = {}
        for key in set().union(self._stored_state.keys(), self._current_state.keys()):
            value = self._get_attr(key)
            try:
                dict = value._recursive_to_dict(seen_refs)
                state[key] = dict
            except AttributeError:
                state[key] = value
            except CircularRefException:
                pass #skip circular references
            
            
        return state
    
    def revert_to_stored_state(self):
        self._current_state = copy.copy(self._stored_state)
        
    def update_stored_state(self):
        self._stored_state = copy.copy(self._current_state)
    
    def _set_attr(self, key, value, default_value = None):
        if value is None:
            value = default_value
        
        self._current_state[key] = value
    
    def _get_attr(self, key):
        if key in self._current_state:
            return self._current_state[key]
        elif key in self._stored_state:
            return self._stored_state[key]
        
        raise AttributeError("No attribute: " + key)
        
        
class CircularRefException(Exception):       
    pass
        
        
    