from werkzeug import utils
from werkzeug.exceptions import Unauthorized, Forbidden

from app.models.user import UserDAO
from framework.http.json_http_exception import JSONHTTPException
from framework.models.session import Session, SessionException


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
            #sesh.set_flag(Session.FLAG_IS_ADMIN)
            return sesh.has_flag(Session.FLAG_IS_ADMIN)
        except SessionException:
            return False
    
    def _get_user(self, user_id = None):
        session = self._get_session()
        u = session.user
        
        if user_id is not None and u.id != user_id:
            if not self._is_admin():
                raise Forbidden()
            else:
                #not the logged in user, but we're admin so we have access
                return UserDAO().get(user_id)
        
        return u
        
    
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
                    return utils.redirect("/")
            
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


def not_implemented(f):
    def wrapper():
        raise NotImplementedError()
    
    if not hasattr(f, "meta"):
        f.meta = {} #copy meta from old func
    f.meta["not_implemented"] = True
    wrapper.meta = f.meta
    
    return wrapper

def comment(comment):
    return meta(comment=comment)
def params(parameters):
    return meta(parameters=parameters)
def returns(returns):
    return meta(returns=returns)
def optional_keys(optional_keys):
    return meta(optional_keys=optional_keys)

def meta(comment = None, parameters = None, returns = None, optional_keys = None):
    
    def decorator(f):
        if not hasattr(f, "meta"):
            f.meta = {}
        
        if comment:
            f.meta["comment"] = comment
        if parameters:
            f.meta["parameters"] = parameters
        if returns:
            f.meta["return"] = returns
        if optional_keys:
            f.meta["optional_keys"] = optional_keys
        
        return f
    
    return decorator
    
    

class NoSessionStoreError(SessionException):
    def __str__(self):
        return "SessionStore required to retreive or store session id"
    
    
        
        
        
        