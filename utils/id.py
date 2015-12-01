import time
from framework.storage.redis import Redis
import pprint

class Id:
    """
        We use 64-bit ids which are build from 4 pieces of data:
        
        24 bits - current minute interval (staggered by shard)
        26 bits - current interval increment count 0 to ~67 million
        10 bits - shard id: 0-1023
         4 bits - pool id: 0-15

    """
    
    # June 1st 2015
    START_TIME = 1433116800
    
    # max increments per interval, = 2^26-1 
    MAX_INCR = 67108863
    
    # maximum number of shards per pool 
    # pools may have less, however, NUM_SHARDS 
    # must be divisible by the actual shard count
    NUM_SHARDS = 1024
    
    # 1 minute intervals
    INTERVAL_SECS = 60
    
    #used to decide if id can be sent to js
    MAX_32_BIT_INT = 2147483647
    
    # this is the original 64bit id
    _id = None
    
    # these are the components to an id
    _shard_id = None
    _pool_id = None
    _interval = None
    _increment = None
    
    
    @classmethod
    def dummy(cls, shard_id, pool_id):
        ins = cls()
        ins.set_pool_id(pool_id)
        ins.set_shard_id(shard_id)
        
        return ins
    
    @classmethod
    def next(cls, shard_id, pool_id, number_of_ids=1):
        """"
            Returns one or more ids for the given shard, pool combo
            
            if number_of_ids is 1, will return a integer
            otherwise will return a list of integers
            
            if shard_id is None, will return ids for a single random shard
        """
        
        ret = []
        
        ins = cls()
        
        ins.set_pool_id(pool_id)
        
        # we'll want to allocate a bunch of ids for this shard all at once
        ins.set_shard_id(shard_id)
        ins.set_interval()
        
        incr = ins._get_next_increment(number_of_ids)
        
        
        # let's start from the beginning of our allocation
        start_incr = (incr - number_of_ids + 1) % ins.MAX_INCR
        
        for i in range(number_of_ids):
            ins.set_increment(start_incr + i)
            ret.append(ins.next_id())
        
        
        # if just one id, return as int for convenience        
        if len(ret) == 1:
            return ret[0]
        
        
        return ret 
        
        
    
    def __init__(self, id=None):
        if id is not None:
            self.set_id(id)
    
    def set_id(self, id):
        self._id = id
        self._deconstruct_id()
    
    def get_id(self):
        return self._id
    
    def set_shard_id(self, id):
        self._shard_id = id
    
    def get_shard_id(self):
        return self._shard_id
    
    def set_pool_id(self, id):
        self._pool_id = id
    
    def get_pool_id(self):
        return self._pool_id
    
    def set_interval(self, interval=None):
        if interval is None:
            interval = self._get_current_interval()
        
        self._interval = interval
        
    def get_interval(self):
        return self._interval
    
    def set_increment(self, incr=None):
        if incr is None:
            incr = self._get_next_increment()
        
        self._increment = incr
        
    def get_increment(self):
        return self._increment
    
    def _get_redis_key(self, pool, shard, interval):
        return "ticket:p" + str(pool) + ":s" + str(shard) + ":i" + str(interval)
    
    def _get_current_interval(self):
        if self._shard_id is None:
            raise MissingInfoError()
        
        # get current seconds
        t = int(time.time())
        
        # subtract off start time to save space
        t -= self.START_TIME
        
        # interval starts at a different second for each shard to avoid 
        # too many redis keys expiring in the same second
        t += (self._shard_id % self.INTERVAL_SECS)
        
        # interval changes every 15 minutes
        return t // self.INTERVAL_SECS
        
    def _get_next_increment(self, incr_count=1):
        if self._shard_id is None or self._pool_id is None or self._interval is None:
            raise MissingInfoError()
        
        # key changes every hour, count starts over
        redis_key = self._get_redis_key(self._pool_id , self._shard_id , self._interval)
        
        redis = Redis.get_instance("id_gen")
        pipe = redis.pipeline()
        if incr_count != 1:
            pipe.incrby(redis_key, incr_count)
        else:    
            pipe.incr(redis_key)
        pipe.expire(redis_key, self.INTERVAL_SECS)
        res = pipe.execute()
        
        return res[0]
        
        
    
    def next_id(self):
        if self._shard_id is None or self._pool_id is None:
            raise MissingInfoError()
        
        if self._interval is None:
            self.set_interval()
        
        if self._increment is None:
            self.set_increment()
        
        self._construct_id()
            
        return self._id
    
    def _get_bit_mask(self, num_bits):
        return (2 ** num_bits) - 1
    
    def _deconstruct_id(self):
        try:
            self._pool_id = self._id & self._get_bit_mask(4)
            self._shard_id = (self._id & (self._get_bit_mask(10) << 4)) >> 4
            self._increment = (self._id & (self._get_bit_mask(26) << 14)) >> 14
            self._interval = (self._id & (self._get_bit_mask(24) << 40)) >> 40
        except TypeError:
            raise BadIdError(self._id);
    
    def _construct_id(self):
        for prop in [self._shard_id, self._pool_id,
                     self._interval, self._increment]:
            if prop is None:
                return
            
        # squeeze everything together into a 64 bit int    
        id = (((self._interval & self._get_bit_mask(24)) << 40)
            | ((self._increment & self._get_bit_mask(26)) << 14)
            | ((self._shard_id & self._get_bit_mask(10)) << 4)
            | (self._pool_id & self._get_bit_mask(4)))
        
        self._id = id


class IdException(Exception):
    pass
    
class BadIdError(IdException):
    
    def __init__(self, provided_id):
        super().__init__("Bad Id provided: " + pprint.pformat(provided_id))

class MissingInfoError(IdException):
    
    def __init__(self):
        super().__init__("generating a new id requires shard_id and pool_id to be set")
            
        
        
