from framework.models.authentication import Authentication
from framework.utils.date_utils import DateUtils
from framework.utils.random_token import RandomToken
from framework.models.auth import AuthDAO, InvalidCredentialsException

import datetime
import hashlib
from framework.storage.mysql import MySQL

class TokenAuth(Authentication):
    
    @classmethod
    def new_for_user(cls, user_id):
        
        str_user_id = str(user_id)
        shard_id = MySQL.get_shard_id_for_string(str_user_id)
        id = MySQL.next_id(shard_id)
        
        secret = RandomToken.build(16)
        
        return cls(id, str_user_id, secret, user_id, True)
        
    def __init__(self, id, provider_id, secret, user_id, secret_hashed = False, expires_ts = None, created_ts = None):
        super().__init__(id, str(provider_id), secret, user_id, True, expires_ts, created_ts)
    
    @classmethod
    def parse(cls, token, max_time=3600):
        try:
            provider_id, hash, ts = token.split("_")
        except ValueError:
            raise InvalidTokenException() 
        
        now = DateUtils.datetime_to_unix(datetime.datetime.now())
        
        if int(ts) + max_time < now:
            raise ExpiredTokenException()
        
        return provider_id, hash, int(ts)
                
        
    def _validate_provider_id(self,provider_id):
        return True

    def verify_secret(self, hash, time=None):
        return hash == hashlib.sha256( str(self.secret).encode("utf-8") + str(time).encode("utf-8") ).hexdigest()


    def get_token(self) -> str:
        """
            return String, Int
        """
        time = DateUtils.datetime_to_unix(datetime.datetime.now())
        hash = hashlib.sha256( str(self.secret).encode("utf-8") + str(time).encode("utf-8")  ).hexdigest()
        
        return "_".join([str(self.user_id), hash, str(time)])
    

class InvalidTokenException(InvalidCredentialsException):
    def __str__(self):
        return "Invalid Token"

class ExpiredTokenException(InvalidCredentialsException):
    def __str__(self):
        return "Expired Token"