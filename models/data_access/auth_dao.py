from framework.storage.mysql import MySQL
from framework.models.domain.authentication import Authentication, AuthException
from framework.models.data_access.data_access_object import DataAccessObject, RowDeletedException
from framework.config.config import Config
from app.models.data_access.user_dao import UserDAO
import importlib

class AuthDAO(DataAccessObject):
    
    def __init__(self):
        super().__init__(Authentication)
    
         
    def new_auth(self, auth_class, provider_id, secret, user):
        pid = self._generate_id_from_provider_id(provider_id)
        
        return auth_class(pid, provider_id, secret, user.id, secret_hashed=False)        
        
    
    def get_auth_by_id(self, auth_id, user = None):
        rows = MySQL.get(auth_id).query("SELECT * FROM auth WHERE id=%s", (auth_id,))
        
        if not len(rows):
            raise NoAuthFoundException("id_" + auth_id)
        
        row = rows[0]
        
        if user is None:
            user_dao = UserDAO()
            user = user_dao.get(row['user_id'])
        elif user.id != row['user_id']:
            raise UserAuthMismatchError()
            
        
        auth = self._row_to_model(row)
        auth.update_stored_state()
        
        return auth
            
    
    def get_auth_by_provider_id(self, auth_class, provider_id):
        
        type_id = self._class_to_type_id(auth_class)
        shard_id =  MySQL.get_shard_id_for_string(provider_id)
        
        rows = MySQL.get_by_shard_id(shard_id).query("SELECT * FROM auth WHERE provider_id=%s AND provider_type=%s", (provider_id, type_id))
        
        if not len(rows):
            raise NoAuthFoundException(provider_id)
        
        row = rows[0]
        
        auth = self._row_to_model(row)
        auth.update_stored_state()
        
        return auth
    
    
    def get_auth_for_user(self, user_id, auth_class = None):
        
        cols = ["user_id"]
        vals = [user_id]
        if auth_class is not None:
            auth_type = self._class_to_type_id(auth_class)
            cols.append("provider_type")
            vals.append(auth_type)
        
        rows = self._get("auth_lookup", cols, vals, user_id)
        rows = self._filter_deleted(rows)
        
        return [self._row_to_model(row) for row in rows]
        
        
    
    def save(self, auth):
        if not auth.is_dirty:
            return False
        
        params = self._model_to_row(auth)
        params["deleted"] = 0
        
        result = self._save("auth", params, ["id", "user_id", "secret", "created_ts", "deleted"], auth.id )
        self._save("auth_lookup", params, ["id", "user_id", "secret", "created_ts", "deleted"], auth.user_id)
        
        auth.update_stored_state()
        
        return result
    
    
    def _model_to_row(self, model):
        dict = super()._model_to_row(model)
        dict["provider_type"] = self._class_to_type_id(model.__class__)
        return dict
    
    def _row_to_model(self, row):        
        if row['deleted']:
            raise RowDeletedException()
        
        auth_class = self._type_id_to_class(row['provider_type'])
        auth = auth_class(row['id'], row['provider_id'].decode("utf-8") , row['secret'].decode("utf-8") , row["user_id"], secret_hashed=True)
        
        return auth
    
    def _generate_id_from_provider_id(self,provider_id):
        shard_id = MySQL.get_shard_id_for_string(provider_id)
        return MySQL.next_id(shard_id)


    def _type_id_to_class(self, type_id):
        type_to_class = Config.get("auth", "type_to_class")
        if str(type_id) not in type_to_class:
            raise InvalidAuthTypeError(type_id)
        
        dict = type_to_class[str(type_id)]
        
        module = importlib.import_module(dict["module"])
        
        class_ = getattr(module, dict["class"])
        
        return class_
        
        
    def _class_to_type_id(self, auth_class):
        type_to_class = Config.get("auth", "type_to_class")
        
        for type_id, dict in type_to_class.items():
            if (dict["module"] == auth_class.__module__ and
                    dict["class"] == auth_class.__name__):
                
                return int(type_id)
           
        raise InvalidAuthTypeError(type_id)
        
                
class InvalidAuthTypeError(AuthException):
    _type_id = None
    
    def __init__(self,type_id):
        self._type_id = type_id
    
    
    def __str__(self):
        return ("Invalid auth type provided: " + str(self._type_id) + "."
                " Type id and classes must be configured in auth.json")
        
class UserAuthMismatchError(AuthException):
    def __str__(self):
        return "auth id does not belong to provided user object"

class NoAuthFoundException(AuthException):
    
    _provider_id = None
    
    def __init__(self,provider_id):
        self._provider_id = provider_id
    
    def __str__(self):
        return "auth row for " + self._provider_id + " does not exist"    

