from framework.models.entity import Entity
from framework.utils.associative_array import AssociativeArray
from framework.utils.disjoint_interval import DisjointInterval


class LazyLoadedCollection(Entity): 
    """
        manages partially loaded data from a list of entities
        also manages deltas so changes to the list can be persisted 
        
    """
    
    def __init__(self, sort_order = AssociativeArray.SORT_HI_TO_LO):
        #dict mapping sort_key to entity
        self._set_attr("key_to_id", AssociativeArray(sort_order))
        #dict mapping entity id to sort key
        self._set_attr("id_to_key",{})
        #list of 2-tuples of found sort key ranges inclusive
        self._set_attr("loaded_ranges",DisjointInterval())
        
        
    def add(self, sort_key, entity_id):
        self._set_key(sort_key, entity_id)
        self._add_to_loaded_ranges(sort_key)

    
    def add_range(self, data_dict, more_before = False, more_after = False):
        
        key_range = self._get_key_range(data_dict, more_before, more_after) 
        
        for key, entity_id in data_dict:
            self._set_key(key, entity_id)
        
        self._add_to_loaded_ranges(key_range[0], key_range[1])
    
    
    def remove(self, enity_id):
        kti = self._get_attr("key_to_id")
        itk = self._get_attr("id_to_key")
        
        key = itk[enity_id]
        
        del kti[key]
        del itk[enity_id]
        
    
    def change_sort_key(self, new_sort_key, enity_id):
        self.remove(enity_id)
        self.add(new_sort_key, enity_id)
    
    
    def get_all(self):
        lr = self._get_attr("loaded_ranges")
        
        #we need all the data loaded in order to call this
        if not lr.in_interval(float("-inf"),float("inf")):
            raise DataNotLoadedError()
        
        return self._get_attr("key_to_id").to_list()
    
    
    def get_range(self, offset_key = None, count = None):
        """
            offset_key of None means, start from beginning of data
            count of None means return all data after offset_key
        """
        kti = self._get_attr("key_to_id")
        
        if not self._in_loaded_ranges(offset_key, count):
            raise DataNotLoadedError()
        
        return kti.get_range(offset_key, count)
        
    
    
    def get(self, sort_key):
        kti = self._get_attr("key_to_id")
        
        if not self._in_found_range(sort_key):
            raise DataNotLoadedError()
        
        #throws key error if, sort key doesn't exist in data
        return kti[sort_key]
    
    
    
    def _get_key_range(self, data_dict, more_before = False, more_above = False):
        
        if more_before or more_above:
            kti = self._get_attr("key_to_id")
            
            #get key range from dictionary
            largest_key = None
            smallest_key = None
            
            for key in data_dict.keys():
                if (smallest_key is None or 
                        key < smallest_key):
                    smallest_key = key
                if (largest_key is None or
                        key > largest_key):
                    largest_key = key
        
            key_range =  (smallest_key, largest_key)
            
            # if we know were at the edge of our dataset, then
            # continue to infinity
            if kti.sort_order == AssociativeArray.SORT_LO_TO_HI:
                if not more_before:
                    key_range = (float("-inf"), key_range[1])
                elif not more_above:
                    key_range = (key_range[0], float("inf"))
            else:
                if not more_before:
                    key_range = (key_range[0], float("inf"))
                elif not more_above:
                    key_range = (float("-inf"), key_range[1])

        
        
            return key_range
        else:
            return (float("-inf"), float("inf"))
        
         
         
    
    def _set_key(self, sort_key, entity_id):
        kti = self._get_attr("key_to_id")
        itk = self._get_attr("id_to_key")
        
        if sort_key in kti:
            if kti[sort_key] == entity_id:
                return False
            
            raise SortKeyConfictError()
        
        kti[sort_key] = entity_id
        itk[entity_id] = sort_key
        
        return True
    
    
    
    def _add_to_loaded_ranges(self, start_key, end_key = None):
        lr = self._get_attr("loaded_ranges")
        lr.add_interval(start_key, end_key)
    
    
    def _in_loaded_ranges(self, start_key, count = None):
        lr = self._get_attr("loaded_ranges")
        kti = self._get_attr("key_to_id")
        itk = self._get_attr("id_to_key")
        
        r = kti.get_range(start_key, count)
        last_found = r[len(r) - 1]
        end_key = itk[last_found.id]
        
        return lr.in_interval(start_key, end_key)
        
    
    def _get_removed_keys(self):
        ret = []
        
        if "id_to_key" not in self._stored_state:
            return ret
        
        stored_itk = self._stored_state["id_to_key"]
        current_itk = self._get_attr("id_to_key")
        
        for key in stored_itk:
            if key not in current_itk:
                ret.append(key)
        
        return ret
    
    def _get_added_keys(self):
        ret = []
        
        current_itk = self._get_attr("id_to_key")
        
        if "id_to_key" not in self._stored_state:
            return current_itk.values()
        
        stored_itk = self._stored_state["id_to_key"]
        
        for key in current_itk:
            if key not in stored_itk:
                ret.append(key)
        
        return ret
    
    
    def _get_modified_keys(self):
        ret = {}
        
        if "id_to_key" not in self._stored_state:
            return ret
        
        current_itk = self._get_attr("id_to_key")
        stored_itk = self._stored_state["id_to_key"]
        
        for (id, key) in current_itk.values():
            if id in stored_itk and stored_itk[id] != key:
                ret[stored_itk[id]] = key
        
        return ret
    
    
    def to_dict(self):
        kti = self._get_attr("key_to_id")
        return {
                    "data" : kti.to_dict(),
                    "added" : self._get_added_keys(),
                    "removed" : self._get_removed_keys(),
                    "modified" : self._get_modified_keys()
                }

class SortKeyConfictError(Exception):
    def __init__(self):
        super().__init__("Only one entity per key is permitted, delete before setting")
    
class DataNotLoadedError(Exception):
    def __init__(self):
        super().__init__("Key was out of loaded data range")
        