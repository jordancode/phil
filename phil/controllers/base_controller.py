from framework.models.service.session_service import SessionService
from framework.models.domain.session import Session, SessionException

class BaseController:
    
    __request = None
    __session_store = None
    
    def __init__(self,request,session_store = None):
        self.__request = request
        self.__session_store = session_store
        
    
    def _get_request(self):
        return self.__request
    
    def _get_session_store(self):
        if self.__session_store is None:
            raise NoSessionStoreException()
        
        return self.__session_store
    
    
    def _is_logged_in(self):
        try:
            self._get_session()
            return True  
        except SessionException:
            return False
    
    
    def _is_admin(self):
        try:
            sesh = self._get_session()
            return sesh.has_flag(Session.FLAG_IS_ADMIN)
        except SessionException:
            return False
    
    def _get_session(self):
        #throws NoActiveSessionException, SessionNotFoundException, NoSessionStoreException
        return self._get_session_store().get_session(self._get_request())



def require_login(f):
    """
     decorator to require logged in user for methods of BaseController child classes
    """
    
    def wrapper(self, *args, **kwargs):
        if not self._is_logged_in():
            raise NotLoggedInException()
        
        return f(self, *args, **kwargs)
        
    return wrapper

def require_admin(f):
    """
     decorator to require logged in *admin* user for methods of BaseController child classes
    """
    
    def wrapper(self, *args, **kwargs):
        if not self._is_admin():
            raise NotAdminException()
        
        return f(self, *args, **kwargs)     
    
    return wrapper



class NotLoggedInException(Exception):
    def __str__(self):
        return "This method requires login"

class NotAdminException(Exception):
    def __str__(self):
        return "This method requires admin permissions"

class NoSessionStoreException(SessionException):
    def __str__(self):
        return "SessionStore required to retreive or store session id"
    
    
        
        
        
        