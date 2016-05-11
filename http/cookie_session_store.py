import framework.models.session
from framework.config.config import Config
from framework.http.base_session_store import BaseSessionStore
import logging
import datetime


class CookieSessionStore(BaseSessionStore):
    
    COOKIE_MAX_AGE=630720000
    
    
    _session=None
    
    def _get_cookie_name(self):
        app_name = Config.get("app","app_key")
        
        return app_name + "_s_id"
    
    def _get_token_cookie_name(self):
        app_name = Config.get("app","app_key")
        
        return app_name + "_s_t"   
    
    def _get_cookie_domain(self):
        server_name = Config.get("app",["hosts", "main", "server_name"])
        return "." + server_name
    
    def set_session(self, response, session):
        
        self._session = session
        
        max_expires_ts = datetime.datetime.now() + datetime.timedelta(seconds=self.COOKIE_MAX_AGE)
        if not session.log_out_ts:
            log_out_ts = max_expires_ts
        else:
            log_out_ts = min(
                session.log_out_ts, 
                max_expires_ts
            )
        
        
        response.set_cookie(self._get_cookie_name(), str(session.id), self.COOKIE_MAX_AGE, log_out_ts, '/', self._get_cookie_domain())
        response.set_cookie(self._get_token_cookie_name(), session.token, self.COOKIE_MAX_AGE, log_out_ts, '/', self._get_cookie_domain())
        
        #also set cookies without a domain for iOS
        #response.set_cookie(self._get_cookie_name(), str(session.id), None, session.log_out_ts, '/')
        #response.set_cookie(self._get_token_cookie_name(), session.token, None, session.log_out_ts, '/')
    
    def get_session(self, request):
        
        if not self._session:
                
            logging.getLogger().debug("TRY GET SESSION!")
            logging.getLogger().debug("Cookies:  " + repr(request.cookies))
            try:
                session_id = request.cookies[self._get_cookie_name()]
                token = request.cookies[self._get_token_cookie_name()]
            except KeyError as e:
                logging.getLogger().debug("No session cookie :(")
                raise framework.models.session.NoActiveSessionException()
            
            self._session =  framework.models.session.SessionService().get_active_session(int(session_id), token)
        
        return self._session
        
    
    
    def delete_session(self, response):
        
        self._session = None
        
        response.delete_cookie(self._get_cookie_name(),'/', self._get_cookie_domain())
        response.delete_cookie(self._get_token_cookie_name(),'/', self._get_cookie_domain())
        
        #also set cookies without a domain for iOS
        #esponse.delete_cookie(self._get_cookie_name(),'/')
        #response.delete_cookie(self._get_token_cookie_name(),'/')
        
