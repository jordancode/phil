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
        
        return auth_class(pid, provider_id, secret, user, False)        
        
    
    def get_auth_by_id(self, auth_id, user = None):
        rows = MySQL.get(auth_id).query("SELECT * FROM auth WHERE id=%s", (auth_id,))
        
        if not len(rows):
            raise NoAuthFoundException("id_" + auth_id)
        
        row = rows[0]
        
        if row['deleted']:
            raise RowDeletedException()
        
        
        if user is None:
            user_dao = UserDAO()
            user = user_dao.get(row['user_id'])
        elif user.id != row['user_id']:
            raise UserAuthMismatchError()
        
        auth_class = self._type_id_to_class(row['provider_type'])
            
        auth = auth_class(row['id'], row['provider_id'].decode("utf-8") , row['secret'].decode("utf-8") , user, True)
        auth.update_stored_state()
        
        return auth
            
    
    def get_auth_by_provider_id(self, auth_class, provider_id):
        
        type_id = self._class_to_type_id(auth_class)
        shard_id =  MySQL.get_shard_id_for_string(provider_id)
        
        rows = MySQL.get_by_shard_id(shard_id).query("SELECT * FROM auth WHERE provider_id=%s AND provider_type=%s", (provider_id, type_id))
        
        if not len(rows):
            raise NoAuthFoundException(provider_id)
        
        row = rows[0]
        
        if row['deleted']:
            raise RowDeletedException()
        
        user_dao = UserDAO()
        user = user_dao.get(row['user_id'])
        
        auth = auth_class(row['id'], provider_id , row['secret'].decode("utf-8") , user, True)
        auth.update_stored_state()
        
        return auth
    
    
    def save(self, auth):
        
        if not auth.is_dirty:
            return False
        
        
        # in this case, if we conflict it will be based on provider_id, provider_type with a deleted row
        # we want to update the id of this row along with create ts
        query = ( "INSERT INTO auth VALUES("
                 "%(id)s,%(user_id)s,%(provider_id)s,%(secret)s,%(provider_type)s,NOW(),%(deleted)s"
                 ") ON DUPLICATE KEY UPDATE "
                 "id=VALUES(id), user_id=VALUES(user_id), secret=VALUES(secret)," 
                 "created_ts=VALUES(created_ts), deleted=VALUES(deleted)" )
        
        
        params = auth.to_dict()
        params["provider_type"] = self._class_to_type_id(auth.__class__)
        params["deleted"] = 0
        del params["user"]
        params["user_id"] = auth.user.id
        
        result = MySQL.get(auth.id).query(query, params)
        auth.update_stored_state()
        
        return result
     
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
    

class InvalidCredentialsException(AuthException):
    def __str__(self):
        return "Credentials are invalid"  
