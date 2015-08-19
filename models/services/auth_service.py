from framework.models.data_access.data_access_object import RowDeletedException
from framework.models.data_access.auth_dao import AuthDAO, NoAuthFoundException
from framework.models.data_access.session_dao import SessionDAO
from framework.models.domain.authentication import AuthException


class AuthService:
    
    def log_in(self, auth_class, provider_id, secret, user_agent):
        """
           returns a user_id
           else throws an authentication exception
        """
        
        dao = AuthDAO()
        
        #throws NoAuthFoundException
        auth = dao.get_auth_by_provider_id(auth_class, provider_id)
        
        if not auth.verify_secret(secret):
            raise InvalidCredentialsException()
        
        session_dao = SessionDAO()
        
        session = session_dao.new_session(auth, user_agent)
        session_dao.save(session)
        
        return session
        
        
    
    def add_auth_to_user(self, user, auth_class, provider_id, secret, user_agent ):
        """
           returns a session
           else throws an authentication exception
        """
        
        dao = AuthDAO()
        
        try:
            auth = dao.get_auth_by_provider_id(auth_class, provider_id)
            
            raise ProviderIdTakenException(provider_id)
            
        except (NoAuthFoundException, RowDeletedException):
            pass
        
        # can throw exceptions if these credentials don't work
        auth = dao.new_auth(auth_class, provider_id, secret, user)
        dao.save(auth)
        
        session_dao = SessionDAO()
        
        session = session_dao.new_session(auth, user_agent)
        session_dao.save(session)
        
        return session


class InvalidCredentialsException(AuthException):
    
    def __str__(self):
        return "Invalid Credentials"    

class ProviderIdTakenException(AuthException):
    
    _provider_id = None
    
    def __init__(self,provider_id):
        self._provider_id = provider_id
    
    def __str__(self):
        return self._provider_id + " is already taken"  

       
    
