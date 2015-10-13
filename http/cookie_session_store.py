from framework.http.base_session_store import BaseSessionStore
from framework.models.services.session_service import SessionService, NoActiveSessionException
from framework.models.domain.session import SessionException
from framework.config.config import Config

class CookieSessionStore(BaseSessionStore):
    
    def _get_cookie_name(self):
        app_name = Config.get("app","app_key")
        
        return app_name + "_s_id"
    
    def _get_token_cookie_name(self):
        app_name = Config.get("app","app_key")
        
        return app_name + "_s_t"   
    
    def _get_cookie_domain(self):
        server_name = Config.get("app","server_name")
        return "." + server_name
    
    def set_session(self, response, session):
        
        response.set_cookie(self._get_cookie_name(), str(session.id), None, session.log_out_ts, '/', self._get_cookie_domain())
        response.set_cookie(self._get_token_cookie_name(), session.token, None, session.log_out_ts, '/', self._get_cookie_domain())
    
    
    def get_session(self, request):  
        try:
            session_id = request.cookies[self._get_cookie_name()]
            token = request.cookies[self._get_token_cookie_name()]
        except KeyError:
            raise NoActiveSessionException()
        
        return  SessionService().get_active_session(int(session_id), token)
        
    
    
    def log_out_session(self, response):
        
        response.delete_cookie(self._get_cookie_name())
        response.delete_cookie(self._get_token_cookie_name())
        
