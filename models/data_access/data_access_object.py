from framework.utils.singleton import Singleton


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
    
    def remove_from_cache(self, model):
        del self._model_cache[model.id]

    def save(self, model):
        #override 
        #checks for dirty keys on the model and updates the database
        model.update_initial_state(None)
        pass
        
    def delete(self,model):
        #override, either deletes the row from the db or sets the deleted flag on it
        #then sets the deleted flag on the model
        model.is_deleted = True

class RowNotFoundException(Exception):
    def __str__(self):
        return "Row could not be found"   
        
class RowDeletedException(Exception):
    
    def __str__(self):
        return "Cannot access deleted row"  
