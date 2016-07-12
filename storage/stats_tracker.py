import hashlib
import logging

from statsd.client import TCPStatsClient
from user_agents import parse

from framework.config.config import Config


class StatsTracker(TCPStatsClient):
    
    _ua_string=None
    
    def __init__(self, ua_string=None):
        config = Config.get("statsd")
        super().__init__(**config)
        self._ua_string=None
    
    
    def _send(self, data):
        try:
            super()._send(data)
        except Exception as e:
            logging.getLogger().warn("Stats tracking failed, connection error")
            self.close()
    
    def track(self, event, count=1):
        
        self.incr(event, count)
        self._incr_platform(event, count, 1)
        
    
    
    def incr(self, stat, count=1, rate=1):
        super().incr(stat,count,rate)
        self._incr_platform(stat,count,rate)
        
        
    
    def verify_checksum(self, event, count, sample, checksum):
        if not checksum:
            return False
        
        key = (str(event) + ":" + str(count) + ":" + str(sample)).encode("utf-8")
        
        return hashlib.md5(key).hexdigest().lower() == checksum.lower()
    
    
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
            
    
            
        
        
        