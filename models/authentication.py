import string
from _datetime import datetime

import bcrypt

from framework.models.entity import Entity


class Authentication(Entity):
    """
      maps user_id's to credentials
    """
    
    @classmethod
    def get_api_class(cls):
        return None
    
    @classmethod
    def get_user_data_from_auth_response(cls, auth_response):
        """
         Translates what's provided to the auth controller into credentials
        """
        pass
    

    def __init__(self, id, provider_id, secret, user_id, secret_hashed = False, expires_ts = None, created_ts = None):
        super().__init__(id)

        self._validate_provider_id(provider_id)
        self._set_attr("provider_id", provider_id)
        self._set_secret(secret,secret_hashed)
        
        self._set_attr("user_id", user_id)
        
        self._set_attr("expires_ts",expires_ts)
        self._set_attr("created_ts",created_ts, datetime.now())
    
    
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
    
    def _set_secret(self, secret, is_hashed=False):
        if not is_hashed:
            self._validate_secret(secret)
            self._set_attr("secret", self._hash_secret(secret))
        else:
            self._set_attr("secret", secret)
    
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
        self._set_secret(new_secret, False)
    
    @property
    def credentials(self):
        return self.secret
    
    
    @property
    def user(self):
        import app.models.user
        return app.models.user.UserDAO().get(self.user_id)
    
    @property
    def created_ts(self):
        return self._get_attr("created_ts")
    
    def is_expired(self):
        return (self._get_attr("expires_ts") is not None and
                datetime.now() > self._get_attr("expires_ts"))
    @property
    def expires_ts(self):
        return self._get_attr("expires_ts")
        
        
    def to_dict(self, for_client = False, optional_keys=None, for_api=False):
        ret = super().to_dict(for_client,optional_keys,for_api)
        if for_client:
            del(ret["secret"])
            
        return ret
    
    def verify_secret(self, new_secret, time=None):
        if not self._get_attr("secret"):
            return False
        
        old_secret = self._get_attr("secret").encode("utf-8")
        new_secret = new_secret.encode('utf-8')
        
        #override if you want to do a different validation
        return not self.is_expired() and (bcrypt.hashpw(new_secret, old_secret) == old_secret)
    
    def _hash_secret(self, secret):
        #override if we don't need to encrypt
        return bcrypt.hashpw(secret.encode('utf-8'),bcrypt.gensalt())
    
    def reauth(self):
        pass
    
    def disconnect(self):
        #used by child classes to disconnect from 3rd party service
        try:
            return self.get_api().revoke_permissions()
        except Exception:
            pass
        
        return False
    
    def get_api(self):
        api_cls = self.get_api_class()
        if api_cls is not None:
            return api_cls().get_for_user(self.credentials)
        return None
    
    def after_login(self):
        pass
    
    def after_connect(self):
        pass
    

class AuthException(Exception):
    def get_friendly_message(self):
        return "An error occurred."

class InvalidSecretException(AuthException):
  
    def __str__(self):
        return "Secret is in an invalid format"
    
    def get_friendly_message(self):
        return "Passwords must be at least 6 characters long."
  
class InvalidProviderIdException(AuthException):
  
    def __str__(self):
        return "Provider Id is in an invalid format"
    
    def get_friendly_message(self):
        return "Please enter a valid email address."
