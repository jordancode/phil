import hashlib

from user_agents import parse

from framework.models.entity import Entity


class UserAgent(Entity):
    
    _parsed = None
    
    @staticmethod
    def generate_hash(ua_string):
        return hashlib.md5(ua_string.encode("utf-8")).digest()     
    
    def __init__(self, id, string):
        super().__init__(id)
        self._set_attr("string", string)
        self._set_attr("hash", UserAgent.generate_hash(string))    
        self._parsed = parse(string)
        
    @property
    def string(self):
        return self._get_attr("string")
    
    @property
    def hash(self):
        return self._get_attr("hash")
    
    @property
    def is_native(self):
        #override to look for 
        return False       
    
    @property
    def is_iOS(self):
        return self._parsed.os.family == "iOS" 
    
    @property
    def is_android(self):
        return self._parsed.os.family == "Android" 
    
    
    def __getattr__(self, key):
        """
            allows access to library attributes
        """
        return getattr(self._parsed,key)
    