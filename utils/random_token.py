import random
import string

from framework.storage.mysql import MySQL
from framework.storage.mysql_pool import MySQLPool
from framework.utils.id import Id


class RandomToken:
    
    MIN_LENGTH = 8
    
    @classmethod
    def build(cls, length, shard_id = None, pool_id = None):
        
        if length < cls.MIN_LENGTH:
            raise Exception("Random token needs to be at least " + str(cls.MIN_LENGTH) + " chars long")
            
        """
        Returns a random alphanumeric string with 
        """
        r = ''.join(random.SystemRandom().choice( (string.ascii_letters + string.digits) ) for _ in range(length))
        
        if shard_id is not None:
            if pool_id is None:
                pool_id = MySQLPool.MAIN
            
            num_shards = MySQL.get_pool(pool_id).get_num_shards()
            shard_id = shard_id % num_shards
            r = cls._apply_shard_info(r, shard_id, pool_id)
        elif pool_id is not None:
            r = cls._apply_shard_info(r, None, pool_id)
        
        return r
    
    @classmethod
    def build_like_id(cls, length, id):
        if isinstance(id, int):
            id = Id(id)
        
        return cls.build(
                length, 
                id.get_shard_id(), 
                id.get_pool_id())
        
    @classmethod
    def get_temp_id_from_token(cls, token):
        hex_str = token[-4:]
        
        i = int(hex_str,16)
        pool_id = i & cls._get_bit_mask(4)
        shard_id = (i & (cls._get_bit_mask(10) << 4)) >> 4
        
        return Id.dummy(shard_id, pool_id)
    
    @classmethod
    def _apply_shard_info(cls, s, shard_id = None, pool_id = None):
        i = 0
        if shard_id is not None:
            i = i | (shard_id << 4)
        if pool_id is not None:
            i = i | pool_id
        
        hex_str = hex(i)[2:]
        
        return s[:-4] + "0000"[len(hex_str):] + hex_str
    
    @classmethod
    def _get_bit_mask(cls, num_bits):
        return (2 ** num_bits) - 1
    