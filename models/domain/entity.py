import copy
import pprint
import logging
from framework.utils.id import Id
from framework.models.domain.serializeable import Serializeable
from framework.utils.type import Type

#Entity shouldn't be an ABC because it can be used stand-alone
class Entity(Serializeable):
    
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
        
        
    def _recursive_to_dict(self, seen_refs, stringify_ids, optional_keys=None):
        d = super()._recursive_to_dict(seen_refs, stringify_ids, optional_keys=optional_keys)
        
        #make sure deleted rows are marked
        if self.deleted:
            d["deleted"] = True
            
        return d
    
    def is_key_dirty(self, key):
        dirty_keys = self.get_dirty_keys()
        
        return key in dirty_keys
        
    def get_dirty_keys(self):
        dirty_keys = {}
        for key in self._get_keys():
            current_val = self._get_attr(key)
            if not key in self._stored_state or self._stored_state[key] != current_val:
                dirty_keys[key] = current_val
        
        return dirty_keys 
    
    def _get_keys(self):
        ret = set().union(self._stored_state.keys(), self._current_state.keys())
        defn = self.get_definition()
        if defn:
            ret = set().union(defn.keys(), ret)
        return ret
    
    
    def revert_to_stored_state(self):
        self._current_state = copy.copy(self._stored_state)
        
    def update_stored_state(self):
        self._stored_state = copy.copy(self._current_state)
    
    def _set_attr(self, key, value, default_value = None):
        if value is None:
            value = default_value
        else:
            #make sure inputs match definition
            d = self.get_definition()
            if d and key in d:
                value = Type.coerce_type(value, d[key].get_type())
        
        self._current_state[key] = value
    
    def _get_attr(self, key):
        if key in self._current_state:
            return self._current_state[key]
        elif key in self._stored_state:
            return self._stored_state[key]
        else:
            return super()._get_attr(key)
        

class InvalidParameterError(Exception):
    def __init__(self, parameter_name, value_provided, expecting_description = None):
        super().__init__(self._create_message(parameter_name, value_provided, expecting_description))
    
    def _create_message(self, param, value, exp = None):
        ret = "Invalid parameter '" + param + "',"
        if exp is not None:
            ret = ret + " expecting " + exp
        
        ret = ret + " but got '" + pprint.pformat(value) + "'"
        
        return ret
        
        
    