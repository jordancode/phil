import hashlib
import logging

from statsd.client import TCPStatsClient
from user_agents import parse

from framework.config.config import Config
from framework.config.app_url import AppUrl
import urllib.parse


class StatsTracker(TCPStatsClient):
    
    _ua_string=None
    
    def __init__(self, ua_string=None):
        config = Config.get("statsd")
        super().__init__(**config)
        self._ua_string=ua_string
    
    
    def _send(self, data):
        return False
        
        try:
            super()._send(data)
        except Exception as e:
            logging.getLogger().warn("Stats tracking failed, connection error")
            logging.getLogger().warn("Would have tracked " + repr(data))
            self.close()
    
    def track(self, event, count=1):
        self.incr(event, count)
    
    def track_bucket(self, event, bucket_indicator, buckets):
        bucket = self._pick_bucket(bucket_indicator, buckets)
        
        self.track(event + "." + bucket)
        
    
    
    def incr(self, stat, count=1, rate=1):
        super().incr(stat,count,rate)
        self._incr_platform(stat,count,rate)
    
    
    def _get_checksum(self, event, count=1, sample=1):
        key = (str(event) + ":" + str(count) + ":" + str(sample)).encode("utf-8")
        return hashlib.md5(key).hexdigest().lower()
        
    
    def verify_checksum(self, event, count, sample, checksum):
        if not checksum:
            return False
        return self._get_checksum(event,count,sample) == checksum.lower()
    
    def track_url(self, event_or_list, next, request=None):
        
        if isinstance(event_or_list, list):
            event_or_list=sorted(event_or_list)
            event_or_list=",".join(event_or_list)
        
        checksum = self._get_checksum(event_or_list)
        next=urllib.parse.quote(next)
        
        return AppUrl().get_current(request) + "/r?checksum="+checksum+"&event="+event_or_list+"&next="+next
    
    
    def _incr_platform(self, event, count=1, rate=1):
        if not self._ua_string:
            return
        
        family = parse(self._ua_string).os.family
        
        if family == "Android":
            event = event+"._android"
        elif family == "iOS":
            event = event+"._ios"
        else:
            event = event+"._desktop"
        
        return super().incr(event, count, rate)
        
        
    def _pick_bucket(self, bucket_indicator, buckets):
        for bucket in buckets:
            if self._in_bucket(bucket_indicator, bucket):
                return self._bucket_to_str(bucket)
        
        return "other"
    
    def _in_bucket(self, bucket_indicator, bucket):
        if isinstance(bucket,tuple) and len(bucket) == 2:
            return bucket_indicator >= bucket[0] and bucket_indicator <= bucket[1]
             
        elif isinstance(bucket, float) or isinstance(bucket, int):
            return bucket_indicator == bucket
        
        return False
            
        
    def _bucket_to_str(self, bucket):
        if isinstance(bucket,tuple) and len(bucket) == 2:
            
            if bucket[0] == float("-inf") and bucket[1] == float("inf"):
                return "all" #dumb bucket, but better than "ltinf"
            elif bucket[0] == float("-inf"):
                return "lt" + str( (bucket [1] + 1) )
            elif bucket[1] == float("inf"):
                return "gt" + str( (bucket [0] - 1) )
            else:
                return str(bucket[0]) + "-" + str(bucket[1])
            
        elif isinstance(bucket, float) or isinstance(bucket, int):
            return str(bucket)
        
        return "other"
        