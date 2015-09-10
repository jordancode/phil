from framework.models.domain.entity import Entity

class UserAlias(Entity):
    
        
    ALIAS_TYPE_EMAIL_ADDRESS = 1
    ALIAS_TYPE_PHONE_NUMBER = 2
    ALIAS_TYPE_FB_ID = 3
    
    
    def __init__(self,provider_id, alias_type, user = None):
        self._set_attr("provider_id", provider_id)
        self._set_attr("alias_type", alias_type)
        self._set_attr("user",user)
        
    @property
    def get_user(self):
        return self._get_attr("user")
    
    def has_user(self):
        return self._get_attr("user") is not None
    
    def get_provider_id(self):
        return self._get_attr("provider_id")
    
    def get_alias_type(self):
        return self._get_attr("alias_type")
    