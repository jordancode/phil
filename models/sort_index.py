import datetime

from framework.storage.redis import Redis
from framework.utils.date_utils import DateUtils
import math


class SortIndex:
    """
        We use 64-bit ids which are build from 2 pieces of data:
        
        32 bits - current second interval
        32 bits - current interval increment count 0 to ~4.3B
        
        SortIndeces should be unique per parent_id 
        (i.e. user_id in user_has_media or user_has_album, album_id in album_has_media)
    
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
    def get_between(cls, si1, si2, parent_id):
        
        #make sure si1,si2 are actually of type SortIndex (not ints)
        to_order=[]
        for si in [si1,si2]:
            if not isinstance(si, SortIndex):
                si = SortIndex(si)
            to_order.append(si)
        si1,si2=sorted(to_order, key=lambda si: si.get_value(), reverse=True)
        
        #create an average sort index
        ret = SortIndex()
        ret.set_time( math.floor( (si1.get_time() + si2.get_time()) / 2) )
        ret.set_incr(cls.get_next_incr(parent_id))
        
        #if it's the same as an existing one, then throw an error
        rv = ret.get_value()
        if rv >= si1.get_value() or rv <= si2.get_value():
            raise NoGapError()
        
        return ret
        

    @classmethod
    def get_for_date(cls, parent_id, dt=None):
        sort_index = cls()
        if dt is None:
            dt = datetime.datetime.now()
        sort_index.set_date(dt)
        sort_index.set_incr(cls.get_next_incr(parent_id))

        return sort_index
    
    @classmethod
    def get_first_in_month(cls, dt=None):
        
        #make this the first of the month
        dt = dt.replace(day=1,hour=0,minute=0,second=0)
        
        #month rollups have 0 incr
        sort_index  =  cls()
        sort_index.set_date(dt)
        sort_index.set_incr(0)
        
        return sort_index
    

    @classmethod
    def get_next_incr(cls, parent_id, incr_count=1):

        # redis_key is per user_id
        redis_key = cls._get_redis_key(parent_id)

        redis = Redis.get_instance("sort_index")

        if incr_count != 1:
            res = redis.incrby(redis_key, incr_count)
        else:
            res = redis.incr(redis_key)

        # increment bits in reverse to maximize space between sort indeces
        return cls._reverse_bits(res, 32)

    @classmethod
    def _reverse_bits(cls, int_to_flip, result_length):
        ret = 0

        for i in range(result_length):
            # start at end of integer,
            current_bit = (int_to_flip >> (result_length - i - 1)) & 0b1
            ret = ret | (current_bit << i)

        return ret

    @classmethod
    def _get_redis_key(cls, parent_id):
        return "sort_index:u" + str(parent_id)

    def __init__(self, sort_index_long=None):
        if sort_index_long is not None:
            self.set_value(sort_index_long)

    def set_value(self, value):
        # turn strings to ints
        value = int(value)

        self._value = value
        self._deconstruct_value()

    def get_value(self):
        if self._value is None:
            self._construct_value()
        return self._value

    def set_date(self, dt=None):
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

    def set_incr(self, incr):
        self._incr = incr

    def get_incr(self):
        return self._incr

    def _get_bit_mask(self, num_bits):
        return (2 ** num_bits) - 1

    def _deconstruct_value(self):
        try:
            self._incr = self._value & self._get_bit_mask(32)
            self._ts = (self._value & (self._get_bit_mask(32) << 32)) >> 32
        except TypeError:
            raise BadSortIndexError(self._value)

    def _construct_value(self):

        for prop in [self._ts, self._incr]:
            if prop is None:
                return

        # squeeze everything together into a 64 bit int    
        sort_index = (((self._ts & self._get_bit_mask(32)) << 32)
                      | (self._incr & self._get_bit_mask(32)))

        self._value = sort_index


class NoGapError(Exception):
    def __init__(self):
        super().__init__("No gap between sort indices")


class BadSortIndexError(Exception):
    def __init__(self, value):
        super().__init__("Bad sort index: " + str(value))
