from framework.config.config import Config
from framework.storage.mysql_shard import MySQLShard
from framework.storage.mysql_transaction import MySQLTransaction
import logging

class MySQLPool:
    
    MAIN = 0
    
    _id = None
    _shards = None
    _config = None
    
    _stoc = False
    
    
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
    
    @property
    def start_transaction_on_connect(self):
        return self._stoc;
    
    @start_transaction_on_connect.setter
    def start_transaction_on_connect(self, boolean):
        self._stoc = boolean;
    
    def get_config_for_shard(self, shard_id):
        box_list = self._config["phys_shards"]
        for box_config in box_list:
            if shard_id >= box_config['min_virt_shard'] and shard_id <= box_config['max_virt_shard']:
                
                return box_config
        
        raise ShardIdOutOfRangeError()
    
    def start_transaction(self):
        self.start_transaction_on_connect = True
        for shard in self._shards.values():
            shard.start_transaction()
    
    def commit(self):
        self.start_transaction_on_connect = False
        for shard in self._shards.values():
            shard.commit()
    
    def rollback(self):
        logging.getLogger().warn("----- ROLLBACK -----")
        
        self.start_transaction_on_connect = False
        for shard in self._shards.values():
            shard.rollback()
    
    @property     
    def transaction(self):
        return MySQLTransaction(self)
    
class ShardIdOutOfRangeError(Exception):
    
    def __str__(self):
        return "Shard id is out of range"