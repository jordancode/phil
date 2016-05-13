import hashlib
import logging

from statsd.client import TCPStatsClient

from framework.config.config import Config


class StatsTracker(TCPStatsClient):
    
    def __init__(self):
        config = Config.get("statsd")
        super().__init__(**config)
    
    
    def _send(self, data):
        try:
            super()._send(data)
        except Exception as e:
            logging.getLogger().warn("Stats tracking failed, connection error")
            self.close()
    
    def track(self, event):
        return self.incr(event)
        
    
    def verify_checksum(self, event, count, sample, checksum):
        key = (str(event) + ":" + str(count) + ":" + str(sample)).encode("utf-8")
        
        return hashlib.md5(key).hexdigest() == checksum
        
        