from redlock import RedLock

from framework.storage.redis import Redis

TTL = 30000
NUM_RETRIES = 30
RETRY_DELAY = 1000

class Lock:
    
    @classmethod
    def get(cls, 
            lock_name, 
            retry_times=RETRY_DELAY,
            retry_delay=RETRY_DELAY,
            ttl=TTL):
        
        
        return RedLock(
                resource=lock_name, 
                connection_details=[Redis.get_instance("main")],
                retry_times=retry_times,
                retry_delay=retry_delay,
                ttl=ttl
            ) 

def withlock(lock_name, retry_times=NUM_RETRIES,retry_delay=RETRY_DELAY,ttl=TTL):
    """
    Decorator function for convenience
    """
    #returns the real decorator
    def decorator(f):
        
        def wrapper(self, *args, **kwargs):
            with Lock.get(lock_name,retry_times,retry_delay,ttl):
                return f(self, *args, **kwargs)
        
        return wrapper
    
    return decorator