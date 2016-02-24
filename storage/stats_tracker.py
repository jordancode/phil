from statsd.client import TCPStatsClient
from framework.config.config import Config
import logging
import hashlib

class StatsTracker(TCPStatsClient):
    
    def __init__(self):
        config = Config.get("statsd")
        super().__init__(**config)
    
    
    def _send(self, data):
        try:
            super()._send(data)
        except Exception as e:
            logging.getLogger().warn("Stat failed")
            logging.getLogger().exception(e)
            self.close()
            
    
    def verify_checksum(self, event, count, sample, checksum):
        key = (str(event) + ":" + str(count) + ":" + str(sample)).encode("utf-8")
        
        return hashlib.md5(key).hexdigest() == checksum
        
        