from framework.models.data_access.session_dao import SessionDAO, SessionNotFoundException
from framework.models.domain.session import Session, SessionException


class SessionService:
    
    
    def log_out(self, session_id):
        dao = SessionDAO()
        session = self.get_active_session(session_id)
        
        session.log_out()
        dao.save_session(session)
        
    
    def get_active_session(self, session_id):
        dao = SessionDAO()
        
        #throws SessionNotFoundException
        session = dao.get_session(session_id)
        
        if session.is_logged_out():
            raise NoActiveSessionException()
        
        return session
    


class NoActiveSessionException(SessionException):
    
    def __str__(self):
        return "No active session"