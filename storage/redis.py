from redis import StrictRedis, ConnectionPool
from framework.config.config import Config
from copy import copy
from pprint import pprint

class Redis(StrictRedis):
    
    """
        Contains static instances to one connection pool per database number
        This can be useful for sharding a redis instance or creating test instances
    """
    
    
    _connection_pools = None
    
    @classmethod
    def get_instance(cls, db_name = "main"):
        if cls._connection_pools is None:
            cls._connection_pools = {}
        
        dbs = Config.get("redis","dbs")

        if not db_name in dbs:
            raise NotARedisDBError(db_name,dbs)
        
        db_number = dbs[db_name]
        
        
        if not db_number in cls._connection_pools:
            cfg = copy(Config.get("redis","connection"))
            cfg["db"] = db_number
            cls._connection_pools[db_number] = ConnectionPool(**cfg)
        
        ins =  cls(connection_pool=cls._connection_pools[db_number])
        
        return ins
        
class NotARedisDBError(Exception):
    
    _db_name = None
    _dbs = None
    
    def __init__(self,db_name,dbs):
        self._db_name = db_name
        self._dbs = dbs
    
    def __str__(self):
        return self._db_name + " is not a redis db, use one of: " + ",".join(list(self._dbs.keys()))