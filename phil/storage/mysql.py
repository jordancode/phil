from framework.storage.mysql_pool import MySQLPool
from framework.storage.mysql_shard import MySQLShard
from framework.utils.id import Id
import random
import hashlib

class MySQL:
    
    _pools = None
    
    
    
    @classmethod
    def get_shard_id_for_string(cls, string, pool_id = None):
        if pool_id is None:
            pool_id = MySQLPool.MAIN
            
        pool = cls.get_pool(pool_id)
        
        #use python built-in hash for this
        md5 = int(hashlib.md5(string.encode("utf-8")).hexdigest(),16) 
        
        
        return md5 % pool.get_num_shards()
        
        
    
    @classmethod
    def get(cls, id):
        if not isinstance(id,Id):
            id = Id(id) 
         
        shard = id.get_shard_id()
        pool_id = id.get_pool_id()
        
        pool = cls.get_pool(pool_id)
        
        return pool.get_shard(shard) 
    
    @classmethod
    def get_by_shard_id(cls, shard_id, pool_id = None):
        if pool_id is None:
            pool_id = MySQLPool.MAIN
        
        pool = cls.get_pool(pool_id)
        
        return pool.get_shard(shard_id)
    
    @classmethod
    def get_pool(cls,pool_id):
        if cls._pools is None:
            cls._pools = {}
        
        if not pool_id in cls._pools:
            cls._pools[pool_id] = MySQLPool(pool_id)
            
        return cls._pools[pool_id]
    
    
    @classmethod
    def next_id(cls,shard_id = None,pool_id = None, number_ids = 1):
             
        if pool_id is None:
            pool_id = MySQLPool.MAIN
        
        pool = cls.get_pool(pool_id)
        
        #pick a random shard id if one wasn't provided
        if shard_id is None:
            shard_id = random.randrange(0, pool.get_num_shards())
        
        return Id.next(shard_id, pool_id, number_ids)
        