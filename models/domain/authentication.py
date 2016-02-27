from passlib.hash import bcrypt
from framework.models.domain.entity import Entity
import string
import logging
from app.models.data_access.user_dao import UserDAO
from _datetime import datetime


class Authentication(Entity):
    """
      maps user_id's to credentials
    """
    

    def __init__(self, id, provider_id, secret, user_id, secret_hashed = False, expires_ts = None):
        super().__init__(id)
        
        self._validate_provider_id(provider_id)
        self._set_attr("provider_id", provider_id)
        
        if not secret_hashed:
            self._validate_secret(secret)
            secret = self._hash_secret(secret)
            
        self._set_attr("secret", secret)
        self._set_attr("user_id", user_id)
        self._set_attr("expires_ts",expires_ts)
    
    
    def _validate_secret(self,secret):
        #something like this may make sense for passwords
        #override in child classes
        if len(secret) < 6 or len(secret) > 255:
            raise InvalidSecretException()
        
        
    def _validate_provider_id(self,provider_id):
        #something like this may make sense for user names
        #override in child classes
        allowed = set(string.ascii_lowercase + string.digits + '._')
        if len(provider_id) > 255 or not (set(provider_id) <= allowed):
            raise InvalidProviderIdException()
    
        
    @property
    def user_id(self):
        return self._get_attr("user_id")
    
        
    @property
    def provider_id(self):
        return self._get_attr("provider_id")
    
    @property
    def secret(self):
        return self._get_attr("secret")
    
    @secret.setter
    def secret(self, new_secret):
        self._validate_secret(new_secret)
        self._set_attr("secret", self._hash_secret(new_secret))
    
    
    @property
    def user(self):
        return UserDAO().get(self.user_id)
    
    
    def is_expired(self):
        return (self._get_attr("expires_ts") is not None and
                datetime.now() > self._get_attr("expires_ts"))
    @property
    def expires_ts(self):
        return self._get_attr("expires_ts")
        
        
    def to_dict(self, for_client = False, optional_keys=None):
        ret = super().to_dict(for_client)
        if for_client:
            del(ret["secret"])
            
        return ret
    
    def verify_secret(self, new_secret):
        #override if you want to do a different validation
        return not self.is_expired() and bcrypt.verify(new_secret, self._get_attr("secret"))
    
    def _hash_secret(self, secret):
        
        #override if we don't need to encrypt
        return bcrypt.encrypt(secret)

class AuthException(Exception):
    pass

class InvalidSecretException(AuthException):
  
    def __str__(self):
        return "Secret is in an invalid format"
  
class InvalidProviderIdException(AuthException):
  
    def __str__(self):
        return "Provider Id is in an invalid format"    
