from framework.models.data_access.data_access_object import DataAccessObject,\
    RowNotFoundException

class EntityRelationDAO(DataAccessObject):

    
    
    def __init__(self, class_, table_name, id1_name, id2_name, columns):
        super().__init__(class_)
        
        self._table_name = table_name
        self._id1_name = id1_name
        self._id2_name = id2_name
        
        self._columns = columns
        self._columns[id1_name] = False
        self._columns[id2_name] = False
    
    
    def _get_one(self, id1, id2):
        rows = self._get(
                  self._table_name, 
                  [self._id1_name, self._id2_name], 
                  [id1, id2], 
                  id1
                )
        
        if not len(rows):
            raise RowNotFoundException()
        
        return rows[0]
    
    def _get_list(self, id1, count = None, offset = None):
        rows = self._get(
                  self._table_name, 
                  [self._id1_name], 
                  [id1],
                  id1,
                  "sort_index",
                  count,
                  offset
                )
        
        return rows
    
    def _get_list_inv(self, id2, count = None, offset = None):
        rows = self._get(
                  self._table_name + "_inv", 
                  [self._id2_name], 
                  [id2], 
                  id2,
                  "sort_index",
                  count,
                  offset
                )
        
        return rows
    
    
    def save(self, model):
        dict_ = self._model_to_row(model)
        
        cols_to_update = [key for key,value in self._columns.items() if value]
        
        self._save( self._table_name, dict_, cols_to_update, model.id1)
        self._save( self._table_name + "_inv", dict_, cols_to_update, model.id2)
        
        model.update_stored_state()
        
        return True
        
        
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
        
        return True
    
    