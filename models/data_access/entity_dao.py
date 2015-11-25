from framework.models.data_access.data_access_object import DataAccessObject,\
    RowNotFoundException
from framework.storage.mysql import MySQL
from framework.utils.multi_shard_query import MultiShardQuery
import pprint
import logging

class EntityDAO(DataAccessObject):
    
    _table = None
    
    def __init__(self, entity_class, table_name):
        super().__init__(entity_class)
        self._table = table_name
    
        
    def get(self, id):
        if self._model_in_cache(id):
            return self._model_cache_get(id)
        
        rows = self._primary_get(id)
        
        if not len(rows):
            raise RowNotFoundException()
        
        model = self._row_to_model(rows[0])
        model.update_stored_state()
        
        self._model_cache_set(model)
        
        return model
        
            
    def _primary_get(self, id):
        return self._get( self._table, ["id"], [id] )
    
    
    def get_list(self, id_list):
        ret = []
        ids_to_find = []
        
        for id in id_list:
            if self._model_in_cache(id):
                ret.append(self._model_cache_get(id))
            else:
                ids_to_find.append(id)
        
        if len(ids_to_find):
            rows = self._primary_get_list(ids_to_find)
            
            rows = self._filter_deleted(rows)
            
            for row in rows:
                model = self._row_to_model(row)
                model.update_stored_state()
                
                self._model_cache_set(model)
                ret.append(model)
        
        return ret
    
    
    def _primary_get_list(self, id_list):
        return MultiShardQuery.multi_shard_in_list_query(
            id_list, "SELECT * FROM " + self._table + " WHERE id in %l")
        
    
    def save(self, model):
        if not model.is_dirty:
            return False
        
        if model.deleted:
            self.remove_from_cache(model.id)
        else:
            self._model_cache_set(model)
        
        dict = self._model_to_row(model)
        ret = self._primary_save(dict)
        
        model.update_stored_state()
        
        logging.getLogger().debug("ABOUT TO SAY RESULT IS: " + pprint.pformat(ret))
        logging.getLogger().debug("ABOUT TO SAY RESULT IS: " + str(ret))
        
        if ret:
            logging.getLogger().debug("HURRAY!")
            return True
        
        return False
    
    def _primary_save(self, dict):
        cols_to_update = [k for k in dict.keys() if (k != "id" and k != "created_ts")]
       
        ret =  self._save(self._table, dict, cols_to_update, dict['id'])
        
        logging.getLogger().debug("EntityDAO.primar_save RESULT: " + str(ret))
        
        return ret
    
    
    def delete(self, id):
        self.remove_from_cache(id)
        
        return self._save(self._table, {"deleted" : 1}, ["deleted"], id)
        
        
        