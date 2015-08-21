from framework.models.data_access.session_dao import SessionDAO, SessionNotFoundException
from framework.models.domain.session import Session, SessionException


class SessionService:
    
    
    def log_out(self, session):
        dao = SessionDAO()
        session.log_out()
        dao.save_session(session)
        
    
    def get_active_session(self, session_id, token):
        dao = SessionDAO()
        
        #throws SessionNotFoundException
        session = dao.get_session(session_id)
        
        if session.is_logged_out():
            raise NoActiveSessionException()
        
        if not session.verify_token(token):
            raise InvalidSessionTokenError()
        
        return session
    
class InvalidSessionTokenError(SessionException):
    def __str__(self):
        return "Session token does not match session id"


class NoActiveSessionException(SessionException):
    
    def __str__(self):
        return "No active session"