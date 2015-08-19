from framework.config.config import Config
from framework.storage.mysql_shard import MySQLShard
from multiprocessing import Pool

class MySQLPool:
    
    MAIN = 0
    
    _id = None
    _shards = None
    _config = None
    
    
    def __init__(self, pool_id = 0):
        self._id = pool_id
        self._shards = {}
        self._config = Config.get("mysql",["pools", str(pool_id)])    
        
        
    def get_shard(self, shard_id):
        if not shard_id in self._shards:
            self._shards[shard_id] = MySQLShard(shard_id, self.get_config_for_shard(shard_id), self);
            
        return self._shards[shard_id]
        
    
    def get_id(self):
        return self._id
    
    
    def get_name(self):
        return self._config["name"]
    
    
    def get_num_shards(self):
        return self._config["num_virt_shards"]
    
    
    def get_config_for_shard(self, shard_id):
        box_list = self._config["phys_shards"]
        for box_config in box_list:
            if shard_id >= box_config['min_virt_shard'] and shard_id <= box_config['max_virt_shard']:
                
                return box_config
        
        raise ShardIdOutOfRangeError()
    
class ShardIdOutOfRangeError(Exception):
    
    def __str__(self):
        return "shard id is out of range"