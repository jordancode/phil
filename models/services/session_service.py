from framework.models.data_access.session_dao import SessionDAO, SessionNotFoundException
from framework.models.domain.session import Session, SessionException


class SessionService:
    
    
    def log_out(self, session):
        dao = SessionDAO()
        session.log_out()
        dao.save(session)
        
    
    def get_active_session(self, session_id, token):
        dao = SessionDAO()
        
        #throws SessionNotFoundException
        session = dao.get_session(session_id)
        
        if session.is_logged_out():
            raise NoActiveSessionException()
        
        if not session.verify_token(token):
            raise InvalidSessionTokenError(token, session.token)
        
        return session
    
class InvalidSessionTokenError(SessionException):
    def __init__(self,):
        super().__init__("Session token does not match")


class NoActiveSessionException(SessionException):
    
    def __str__(self):
        return "No active session"