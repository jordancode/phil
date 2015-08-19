from framework.http.base_session_store import BaseSessionStore
from framework.models.services.session_service import NoActiveSessionException
from framework.config.config import Config

class CookieSessionStore(BaseSessionStore):
    
    def _get_cookie_name(self):
        app_name = Config.get("app","name")
        
        return app_name + "_sess"
    
    def set_session(self, response, session):
        
        response.set_cookie(self._get_cookie_name(), session.id, None, session.log_out_ts)
    
    
    def get_session(self, request):  
        try:
            cookie = request.cookies[self._get_cookie_name()]
        except KeyError:
            raise NoActiveSessionException()
        
        return SessionService().get_active_session(cookie)
    
    
    def log_out_session(self, response, session):
        
        response.delete_cookie(self._get_cookie_name())
        SessionService().log_out(session.id)