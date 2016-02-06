from framework.models.data_access.data_access_object import DataAccessObject,\
    RowNotFoundException
from framework.storage.mysql import MySQL
from framework.utils.multi_shard_query import MultiShardQuery
from framework.utils.query_builder import SQLQueryBuilder
from framework.utils.id import Id
import datetime

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
        
        #sort list by original order since it gets messed up with cache and shards
        list_map = {id : index for index, id in enumerate(id_list)}
        ret = sorted(ret, key=lambda row: list_map.get(row.id))
        
        return ret
    
    
    def _primary_get_list(self, id_list):
        return MultiShardQuery.multi_shard_in_list_query(
            id_list, "SELECT * FROM " + self._table + " WHERE id in %l", None, MySQL.get_pool(self._pool()))
        
    
    def save(self, model):
        return self.save_list([model])
    
    
    def save_list(self, models):
        #saves a list of models with the assumption that they all belong on the same shard
        #otherwise, use save() to save one at a time
        models_to_save = []
        
        for model in models:
            if not model.is_dirty:
                continue
            
            if model.deleted:
                self.remove_from_cache(model.id)
            else:
                self._model_cache_set(model)
            
            models_to_save.append(model)
            model.update_stored_state()
        
        return self._save_list(self._table, models_to_save)
    
    
    def _save_list(self, table, models, shard_by_col = "id"):
        if not len(models):
            return True
                   
        dicts = [self._model_to_row(model) for model in models]
        d = dicts[0]
        
        #distribute dicts to respective shard ids
        shard_id_to_dicts = {}
        for dict_ in dicts:
            id = dict_[shard_by_col]
            shard_id = Id(id).get_shard_id()
            
            if not shard_id in shard_id_to_dicts:
                shard_id_to_dicts[shard_id] = []
                
            shard_id_to_dicts[shard_id].append(dict_)
        
        for shard_id, dict_list in shard_id_to_dicts.items(): 
            
            vals = [ ["%s" for key in dict_ ] for dict_ in dict_list ]
            params = [ value for dict_ in dict_list for key, value in dict_.items() ]
            
            cols_to_update = [
                    (k, "VALUES(" + k + ")")  
                    for k in self._get_columns_to_update(d.keys())
                ]
            
            qb = (SQLQueryBuilder.insert(table)
                  .columns(d.keys())
                  .values(vals)
                  .on_duplicate_key_update(cols_to_update))
            
            mysql = MySQL.get_by_shard_id(shard_id, self._pool())
            mysql.query(qb.build(), tuple(params))
        
        return True 
        
      
    
    def _primary_save(self, dict):
        cols_to_update = [k for k in self._get_columns_to_update(dict.keys())]
       
        ret =  self._save(self._table, dict, cols_to_update, dict['id'])
        
        return ret
    
    
    def _get_columns_to_update(self, all_columns):
        return [k for k in all_columns if (k != "id" and k != "created_ts")]
    
    def delete(self, id):
        self.remove_from_cache(id)
        
        return self._save(self._table, {"id" : id, "deleted" : 1, "modified_ts" : datetime.datetime()}, ["deleted", "modified_ts"], id)
        
        
        