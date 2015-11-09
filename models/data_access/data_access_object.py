from framework.utils.singleton import Singleton
from framework.storage.mysql import MySQL
import logging
from pprint import pformat
import pprint


class DataAccessObject(metaclass=Singleton):
    """
        maintains a list of rows for this model type that have been pulled from the database
        if we fetch a model twice, return a new model using the old row
        in this way, we can tell if any model has 
    """
    
    _model_cache = None
    _model_class = None
    
    
    def __init__(self, model_class):
        self._model_class = model_class
        self._model_cache = {}
        
    def _model_in_cache(self,id):
        return id in self._model_cache

    def _model_cache_get(self,id):
        return self._model_cache[id]
    
    def _model_cache_set(self,id,model):
        assert isinstance(model, self._model_class)
        
        self._model_cache[model.id] = model
    
    
    def next_id(self, id_like = None):
        if id_like:
            return MySQL.next_id_like(id_like)
        
        return MySQL.next_id()
        
    
    
    def remove_from_cache(self, model):
        del self._model_cache[model.id]
    
    def _get(self, table_name, column_list, value_list, shard_by = None, order_by = None, count = None, offset = None):
        sql = (
               "SELECT * FROM " + table_name + " WHERE " 
               + " AND ".join(
                    column_name+"=%s" for column_name in  column_list
                ))
        
        if order_by:
            if offset:
                sql += " AND " + order_by + " > " + offset
            
            sql += " ORDER BY " + order_by
        
        if count:
            sql += " LIMIT " + count
        
        if shard_by is None:
            shard_by = value_list[0]
        
        return MySQL.get(shard_by).query(sql, value_list)    
        
    
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
                     + (" AND ".join(
                            col +"=VALUES("+ col +")" for col in cols_to_update
                    ))
                ) 

        
        if shard_by is None:
            shard_by = col_to_value['id']
        
        return MySQL.get(shard_by).query(sql, col_to_value)    
        
    def _delete(self, table_name, column_list, value_list, shard_by = None):
        
        sql = ("UPDATE " + table_name + " set deleted=1 WHERE "
               + " AND ".join( 
                column_name+"=%s" for column_name in column_list
            ))
        
        logging.getLogger().debug(sql)
        logging.getLogger().debug(pprint.pformat(value_list))
        
        
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
        if "deleted" in row:
            if row["deleted"]:
                raise RowDeletedException()
            else:
                del(row["deleted"])
            
        
        return self._model_class(**row)
    
    def _filter_deleted(self, rows):
        ret = []
        for row in rows:
            if "deleted" not in row or not row["deleted"]:
                ret.append(row)
                
        return ret


class RowNotFoundException(Exception):
    def __init__(self):
        super().__init__("Row could not be found")   
        
class RowDeletedException(Exception):
    
    def __init__(self):
        super().__init__("Cannot access deleted row");
      
