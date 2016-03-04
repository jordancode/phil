from framework.models.data_access_object import DataAccessObject
from framework.models.entity import Entity
from framework.storage.mysql import MySQL

class BaseUserDAO(DataAccessObject):
    
    def __init__(self, _class = None):
        super().__init__(_class or Entity)
    
    """
        minimum interface that a UserDAO will have to implement to be used by the framework auth and session code
    """
    
    def new_user(self,  *args, **kwargs):
        
        return Entity(MySQL.next_id())
    
    def get(self, user_id):
        
        return Entity(user_id)