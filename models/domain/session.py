from framework.models.domain.entity import Entity
from framework.config.config import Config
import datetime
import random
import string

class Session(Entity):
    
    FLAG_IS_ADMIN = 0b1
    
    TOKEN_LENGTH = 20
    
    def __init__(self, id, user, user_agent, auth, created_ts = None, modified_ts = None, log_out_ts = None, flags = None, token = None):
        super().__init__(id)
        
        self._set_attr("user",user)
        self._set_attr("user_agent", user_agent)
        self._set_attr("auth", auth)
        
        self._set_attr("created_ts", created_ts, datetime.datetime.now())
        self._set_attr("modified_ts", modified_ts, datetime.datetime.now())
        self._set_attr("log_out_ts", log_out_ts)
        
        self._set_attr("flags",flags)
        
        if not token:
            token = self.generate_token()
        
        self._set_attr("token",token)
        
    
    def generate_token(self):
        return ''.join(random.SystemRandom().choice( (string.ascii_letters + string.digits) ) for _ in range(self.TOKEN_LENGTH))
    
    def verify_token(self, token_to_check):
        return self.token == token_to_check
    
    @property
    def token(self):
        return self._get_attr("token")
    
    
    
    #########
    @property
    def user(self):
        return self._get_attr("user")
    
    @property
    def user_agent(self):
        return self._get_attr("user_agent")
    
    @property
    def auth(self):
        return self._get_attr("auth") 
    #########
    
    
    
    
    
    def has_flag(self, bit_mask):
        flags = self._get_attr("flags")
        return flags & bit_mask
    
    def set_flag(self, bit_mask, value = True):
        flags = self._get_attr("flags")
        if value:
            self._set_attr("flags", flags | bit_mask)
        else:
            self._set_attr("flags", flags | bit_mask)
   
    def update_session_modified(self):
        self._set_attr("modified_ts", int(datetime.datetime.now()))
        
    def get_time_since_modified(self):
        return datetime.datetime.now() - self._get_attr("modified_ts")
    
    def get_time_since_start(self):
        return datetime.datetime.now() - self._get_attr("start_ts")
    
    
    @property
    def log_out_ts(self):
        return self._get_attr("log_out_ts")
    
    def is_logged_out(self):
        return (
                self._get_attr("log_out_ts") is not None and
                self._get_attr("log_out_ts") <= datetime.datetime.now()
            )
    
    def log_out(self):
        if not self.is_logged_out():
            self._set_attr("log_out_ts", datetime.datetime.now())
 
    
class SessionException(Exception):
    pass   
    
        
    
    
    
        