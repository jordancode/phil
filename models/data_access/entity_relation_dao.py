from framework.models.data_access.data_access_object import DataAccessObject,\
    RowNotFoundException
from framework.utils.multi_shard_query import MultiShardQuery
import logging
from framework.storage.mysql import MySQL
from framework.utils.id import BadIdError
from framework.utils.associative_array import SORT_HI_TO_LO
from framework.utils.query_builder import SQLQueryBuilder, And

class EntityRelationDAO(DataAccessObject):

    
    
    def __init__(self, class_, table_name, id1_name, id2_name, columns):
        super().__init__(class_)
        
        self._table_name = table_name
        self._id1_name = id1_name
        self._id2_name = id2_name
        
        self._columns = columns
        if not id1_name in columns:
            self._columns[id1_name] = False
        if not id2_name in columns:
            self._columns[id2_name] = False
    
    
    
    """
    
    -------- GET STUFF -------
    
    """
    
    
    def _get_one(self, id1, id2):
        cache_id = self._get_cache_id(id1,id2)
        
        if self._model_in_cache(cache_id):
            return self._model_cache_get(cache_id)
        
        rows = self._get(
                  self._table_name, 
                  [self._id1_name, self._id2_name], 
                  [id1, id2], 
                  id1
                )
        
        if not len(rows):
            raise RowNotFoundException()
        
        row = rows[0]
        
        ret = self._row_to_model(row)
        ret.update_stored_state()
        
        self._model_cache_set(ret)
        
        return ret
    
          
    
    def _get_list_primary(self, id1, count = None, offset = None, sort_by = "sort_index", has_permissions = None, missing_permissions = None, sort = SORT_HI_TO_LO):
        rows = self._get_list(
                  self._table_name,
                  id1,
                  self._id1_name,
                  sort_by,
                  count,
                  offset,
                  has_permissions,
                  missing_permissions,
                  sort
                )
        
        return self._parse_rows(rows)
    
    
    
    def _get_list_inv(self, id2, count = None, offset = None, sort_by = "sort_index", has_permissions = None, missing_permissions = None, sort = SORT_HI_TO_LO):
        rows = self._get_list( 
                  self._table_name + "_inv",
                  id2,
                  self._id2_name,
                  sort_by,
                  count,
                  offset,
                  has_permissions,
                  missing_permissions,
                  sort
                )
        
        return self._parse_rows(rows)
    
    
    
    def _get_list(self, table_name, id, id_name, sort_by = "sort_index",count = None, offset = None, has_permissions = None, missing_permissions = None, sort = SORT_HI_TO_LO):

        where_clause = And([
                  (id_name, "=", "%s"),
                  ("deleted", "=", "0")
                  ]);
        
        if has_permissions:
            where_clause.append(
                          ("permission|"+str(has_permissions), "=", "permission" )
                        )
        
        if missing_permissions:
            where_clause.append(
                          ("permission&"+str(missing_permissions), "=", "permission" )
                        )
            
        query_builder = (SQLQueryBuilder
                            .select(table_name)
                            .where(where_clause)
                            .limit(count, offset))
        
        if sort_by:
            query_builder.order_by(sort_by, sort)
        
        try:
            ret = MySQL.get(id).query(query_builder.build(), [id])
        except BadIdError:
            raise RowNotFoundException()
        
        
        return ret
    
    def _parse_rows(self, rows):
        ret = []
        rows = self._filter_deleted(rows)
        
        for row in rows:
            model = self._row_to_model(row)
            self._model_cache_set(model)
            model.update_stored_state()
            
            ret.append(model)
            
        return ret
        
    
    """
    
    -------- SAVE STUFF -------
    
    """    
        
    
    def save(self, model):
        if not model.is_dirty:
            logging.getLogger().debug("NOT DIRTY?")
            return False
        
        dict_ = self._model_to_row(model)
        
        
        cols_to_update = [key for key,value in self._columns.items() if value]
        
        self._save( self._table_name, dict_, cols_to_update, model.id1)
        self._save( self._table_name + "_inv", dict_, cols_to_update, model.id2)
        
        model.update_stored_state()
        self._model_cache_set(model)
        
        return True
    
        
    
    def save_list(self, models):
        if not len(models):
            return 0
        
        models = self._filter_clean(models)
        
        dicts = [self._model_to_row(model) for model in models]
        cols_to_update = [key for key,value in self._columns.items() if value]
        
        row_count = MultiShardQuery(self._pool()).multi_shard_insert(self._table_name, self._id1_name, dicts, cols_to_update)
        row_count = MultiShardQuery(self._pool()).multi_shard_insert(self._table_name+"_inv", self._id2_name, dicts, cols_to_update)
        
        for model in models:
            model.update_stored_state()
            self._model_cache_set(model)
        
        return row_count
    
      
    """
    
    -------- DELETE STUFF -------
    
    """
    
    
    def delete(self, model):
        self._delete(
                  self._table_name, 
                  [self._id1_name, self._id2_name], 
                  [model.id1, model.id2], 
                  model.id1
                )
        
        self._delete(
                  self._table_name + "_inv", 
                  [self._id2_name, self._id1_name], 
                  [model.id2, model.id1], 
                  model.id2
                )
        
        model.is_deleted = True
        
        self.remove_from_cache(self._get_cache_id(model.id1, model.id2))
        
        
        return True
    
    
    def _delete_list_by_primary_id(self, id1):
        models = self._get_list_primary(id1, None, None, None);
        for model in models:
            self.delete(model)
        
        return True
    
    def _delete_list_by_inv_id(self, id2):
        
        models = self._get_list_inv(id2, None, None, None);
        for model in models:
            self.delete(model)
        
        return True
    
    def _get_cache_id(self,id1,id2):
        return str(id1) + "_" + str(id2)
    
