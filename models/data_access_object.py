import logging
from abc import ABCMeta

from framework.storage.mysql import MySQL, MySQLPool
from framework.utils.id import BadIdError
from framework.utils.model_cache import ModelCache
from framework.utils.sql_utils import SQLUtils


class DataAccessObject(metaclass=ABCMeta):
    """
        maintains a list of rows for this model type that have been pulled from the database
        if we fetch a model twice, return a new model using the old row
        in this way, we can tell if any model has 
    """
    
    _model_cache = None
    _model_class = None
    
    _return_deleted = False
    
    
    def __init__(self, model_class):
        self._model_class = model_class
        self._model_cache = ModelCache.get_for_model(model_class.__name__)
        
    def _pool(self):
        return MySQLPool.MAIN
        
        
    def _model_in_cache(self,id):
        return id in self._model_cache

    def _model_cache_get(self,id):
        #if id in self._model_cache:
        #    logging.getLogger().debug("----- CACHE HIT! --- " + self._model_class.__name__ + " " + str(id) )
        
        return self._model_cache[id]
    
    def _model_cache_set(self,model):
        assert isinstance(model, self._model_class)
        #logging.getLogger().debug("----- CACHE SET --- " + self._model_class.__name__ + " " + str(model.id) )
        
        self._model_cache[model.id] = model
    
    
    def next_id(self, id_like = None):
        if id_like:
            return MySQL.next_id_like(id_like, self._pool())
        
        return MySQL.next_id(pool_id=self._pool())
        
    
    def remove_from_cache(self, id):
        del self._model_cache[id]
        
    
    #this is a property so it can be overriden
    @property
    def return_deleted(self):
        return self._return_deleted
    
    @return_deleted.setter
    def return_deleted(self, boolean):
        self._return_deleted = boolean
    
    def _get(self, table_name, column_list, value_list, shard_by = None, order_by = None, count = None, offset = None):
        sql = (
               "SELECT * FROM " + table_name + " WHERE " 
               + " AND ".join(
                    column_name+"=%s" for column_name in  column_list
                ))
        
        if order_by:
            if offset:
                sql += " AND " + order_by + " > " + str(offset)
            
            sql += " ORDER BY " + order_by
        
            if count:
                sql += " LIMIT " + str(count)
        else:
            sql += " " + SQLUtils.get_limit_string(count, offset)
        
        if shard_by is None:
            shard_by = value_list[0]
            
        logging.getLogger().debug(sql)
        
        try:
            ret = MySQL.get(shard_by).query(sql, value_list)
        except BadIdError:
            raise RowNotFoundException()
        
        logging.getLogger().debug("RESULTS: " + str(len(ret)))
        
        return ret
        
    
    def _save(self, table_name, col_to_value, cols_to_update,  shard_by = None):
        #override 
        #checks for dirty keys on the model and updates the database
        
        sql = ( 
               "INSERT INTO " + table_name + "( "
               + ( ", ".join(col_name for col_name in col_to_value.keys()) )  
               + " ) VALUES( "
               + ( ", ".join("%(" + col_name + ")s" for col_name in col_to_value.keys()) ) 
               + " )"
            )
        
        if len(cols_to_update):
            sql = sql + (
                     " ON DUPLICATE KEY UPDATE "
                     + (", ".join(
                            col +"=VALUES("+ col +")" for col in cols_to_update
                    ))
                ) 

        logging.getLogger().debug("SAVE: " + sql)
        if shard_by is None:
            shard_by = col_to_value['id']
        
        ret = MySQL.get(shard_by).query(sql, col_to_value)
        
        logging.getLogger().debug("DAO._save RESULT " + str(ret))
        
        return ret
        
    def _delete(self, table_name, column_list, value_list, shard_by = None):
        
        sql = ("UPDATE " + table_name + " set deleted=1 WHERE "
               + " AND ".join( 
                column_name+"=%s" for column_name in column_list
            ))
        
        
        if not shard_by:
            shard_by = value_list[0]
            
        success = MySQL.get(shard_by).query(sql, value_list)
        
        return success


    def _model_to_row(self, model):
        d = model.to_dict()
        if "object" in d:
            del(d["object"])
            
        return d
    
    def _row_to_model(self, row):
        d = False
        
        if "deleted" in row:
            d = row["deleted"]
            del(row["deleted"])
        
        if d and not self.return_deleted:
            raise RowDeletedException()
            
        ret = self._model_class(**row)
        
        if d:
            ret.set_deleted()
        
        return ret
    
    def _filter_deleted(self, rows):
        ret = []
        for row in rows:
            if "deleted" not in row or not row["deleted"]:
                ret.append(row)
                
        return ret
    
    def _filter_clean(self, models):
        ret = []
        for model in models:
            if model.is_dirty:
                ret.append(model)
        
        return ret

class RowNotFoundException(Exception):
    def __init__(self):
        super().__init__("Row could not be found")   
        
class RowDeletedException(Exception):
    
    def __init__(self):
        super().__init__("Cannot access deleted row")
      
