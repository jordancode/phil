from framework.models.services.session_service import SessionService
from framework.models.domain.session import Session, SessionException
from werkzeug.exceptions import Unauthorized, Forbidden
from framework.http.json_response import JSONResponse
from framework.http.json_http_exception import JSONHTTPException

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
            raise NoSessionStoreError()
        
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
    
    def _get_user(self):
        return self._get_session().user
    
    def _get_session(self):
        #throws NoActiveSessionException, SessionNotFoundException, NoSessionStoreException
        return self._get_session_store().get_session(self._get_request())


def require_login(f = None, return_json=True):
    def decorator(f):
        """
         decorator to require logged in user for methods of BaseController child classes
        """
        
        def wrapper(self, *args, **kwargs):
            if not self._is_logged_in():
                if return_json:
                    raise JSONHTTPException(Unauthorized)
                else:
                    raise Unauthorized()
            
            return f(self, *args, **kwargs)
            
        return wrapper
    
    if f is None:
        return decorator
    else:
        return decorator(f)

def require_admin(f = None, return_json = True):
    def decorator(f):
        """
         decorator to require logged in *admin* user for methods of BaseController child classes
        """
        
        def wrapper(self, *args, **kwargs):
            if not self._is_admin():
                if return_json:
                    raise JSONHTTPException(Forbidden)
                else:
                    raise Forbidden()
            
            return f(self, *args, **kwargs)     
        
        return wrapper
    
    if f is None:
        return decorator
    else:
        return decorator(f)


class NoSessionStoreError(SessionException):
    def __str__(self):
        return "SessionStore required to retreive or store session id"
    
    
        
        
        
        