from framework.storage.redis import Redis
from redlock.lock import RedLockFactory

TTL = 300
NUM_RETRIES = 300
RETRY_DELAY = 1000

class Lock:
    
    _factory=None
    
    
    @classmethod
    def get_factory(cls):
        if not cls._factory:
            cls._factory = RedLockFactory([Redis.get_instance("main")])
        return cls._factory
    
    
    @classmethod
    def get(cls, 
            lock_name, 
            retry_times=RETRY_DELAY,
            retry_delay=RETRY_DELAY,
            ttl=TTL):
        
        return cls.get_factory().create_lock(lock_name, 
            retry_times=RETRY_DELAY,
            retry_delay=RETRY_DELAY,
            ttl=TTL)

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