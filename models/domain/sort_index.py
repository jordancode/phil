from framework.utils.id import MissingInfoError
from framework.storage.redis import Redis
import datetime

    
SORT_INDEX_TYPE_DEFAULT = 0

class SortIndex:
    
    """
        We use 64-bit ids which are build from 4 pieces of data:
        
        32 bits - current second interval
        25 bits - current interval increment count 0 to ~33 million
        7 bits - sort_index type: 0-127

    """
    
    # 1 minute intervals for id generation
    INTERVAL_SECS = 60
    
    # June 1st 2015
    START_TIME = 1433116800
    
    _value = None
    
    _ts = None
    _incr = None
    _type = None
    
    @classmethod
    def get_between(cls, sort_index_start, sort_index_end, type = None):
        if isinstance(sort_index_start,int):
            sort_index_start = cls(sort_index_start)
        
        if isinstance(sort_index_end,int):
            sort_index_end = cls(sort_index_end)
        
        
        if (sort_index_start.get_time() == sort_index_end.get_time() and
                sort_index_start.get_increment() == sort_index_end.get_increment()):
            raise NoGapError()
            
        if type is None:
            type = sort_index_start.get_type()
        
        
        new_ts = sort_index_start.get_time() + int((sort_index_end.get_time() - sort_index_start.get_time())/2)
        
        new_sort_index = cls()
        new_sort_index.set_time(new_ts)
        new_sort_index.set_type(type)
        new_incr = None
        if new_ts == sort_index_start.get_time() or new_ts == sort_index_end.get_time():
            new_incr = int((sort_index_start.get_increment() + sort_index_end.get_increment()) / 2)
            if new_incr ==  sort_index_start.get_increment() or new_incr == sort_index_end.get_increment():
                raise NoGapError()
        
        
        
        return new_sort_index
        
    
    @classmethod
    def get_for_date(cls, datetime, type = SORT_INDEX_TYPE_DEFAULT):
        sort_index = cls()
        sort_index.set_date(datetime)
        sort_index.set_type(type)
        sort_index.set_incr()
        
        return sort_index
    
    
    
    def __init__(self, sort_index_long = None):
        if sort_index_long is not None:
            self.set_value(sort_index_long)
    
    
    def set_value(self, value):
        #turn strings to ints
        value = int(value)
        
        self._value = value
        self._deconstruct_value()
    
    
    def get_value(self):
        if self._value is None:
            self._construct_value()
        return self._value
    
    
    def set_date(self, dt = None):
        if dt is None:
            dt = datetime.datetime.now()
            
        self._ts = DateUtils.datetime_to_unix(dt)
        return self
    
    def get_date(self):
        return DateUtils.unix_to_datetime(self._ts)
    
    
    def set_time(self, ts):
        self._ts = ts
    
    def get_time(self):
        return self._ts
    
    
    def set_type(self, type = SORT_INDEX_TYPE_DEFAULT):
        self._type = type
    
    def get_type(self):
        return self._type
    
    
    def set_incr(self, incr = None):
        if incr is None:
            incr = self._get_next_increment()
            
        self._incr = incr
    
    def get_incr(self):
        return self._incr
    
        
    def _get_next_increment(self, incr_count=1):
        if self._ts is None or self._type is None:
            raise MissingInfoError()
        
        # key changes every hour, count starts over
        redis_key = self._get_redis_key(self._ts, self._type)
        
        redis = Redis.get_instance("id_gen")
        pipe = redis.pipeline()
        
        if incr_count != 1:
            pipe.incrby(redis_key, incr_count)
        else:    
            pipe.incr(redis_key)

        pipe.expire(redis_key, self.INTERVAL_SECS)
        res = pipe.execute()
        
        #increment bits in reverse to maximize space between sort indeces
        return self._reverse_bits(res[0], 25)
    
    
    def _reverse_bits(self, int_to_flip, result_length):
        ret = 0
        
        for i in range(result_length):
            #start at end of integer, 
            current_bit = (int_to_flip >> (result_length - i - 1)) & 0b1
            ret = ret | (current_bit << i)
        
        return ret
        
    
    def _get_bit_mask(self, num_bits):
        return (2 ** num_bits) - 1
    
    def _deconstruct_value(self):
        try:
            self._type = self._value & self._get_bit_mask(7)
            self._incr = (self._value & (self._get_bit_mask(25) << 7)) >> 7
            self._ts = (self._value & (self._get_bit_mask(32) << 32)) >> 32
        except TypeError:
            raise BadSortIndexError(self._value);
    
    def _construct_value(self):
        
        for prop in [self._ts, self._incr, self._type]:
            if prop is None:
                return
            
        # squeeze everything together into a 64 bit int    
        sort_index = (((self._ts & self._get_bit_mask(32)) << 32)
            | ((self._incr & self._get_bit_mask(25)) << 7)
            | (self._type & self._get_bit_mask(7)))
        
        self._value = sort_index

    
    def _get_redis_key(self, ts, type):
        
        interval = ts // 60
        
        return "sort_index:i" + str(interval) + ":t" + str(type) 
        
class NoGapError(Exception):
    def __init__(self):
        super().__in

class BadSortIndexError(Exception):
    def __init__(self, value):
        super().__init__("Bad sort index: " + str(value))
        
    
from framework.utils.date_utils import DateUtils