import pickle
import time
import uuid

import datetime
from rq import Queue
from framework.storage.redis import Redis


class RedisDelay(object):

    def __init__(self, redis = None, queue_name = "default"):
        if redis is None:
            redis = Redis.get_instance("queue")
        self.redis = redis
        
        self.queue_name = queue_name
        
    
    #delay a rq job to run at a datetime
    def date(self, date, job, *args, **kwargs):
        sec = (date-datetime.datetime.now()).total_seconds()
        sec = max(0, sec) #don't allow negative perform times
        return self.delay(self.queue_name, sec, job, *args, **kwargs)
         
    
    
        
    #Delay rq job by seconds
    def delay(self, seconds, job, *args, **kwargs):
        
        #no need to delay if runtime is now
        if seconds <= 0:
            return self.queue(job, *args, **kwargs)
        
        pickled_job = pickle.dumps({
            'job': job, 
            'queue': self.queue_name, 
            'args': args, 
            'kwargs': kwargs, 
            'id': uuid.uuid1().hex
        })
        
        return self.redis.zadd(
            'queue:delayed',  
            int(time.mktime(time.gmtime())) + seconds, 
            pickled_job
        )
    
    #queue job for immediate processing
    def queue(self, job, *args, **kwargs):
        return self._add_to_queue(job, self.queue_name, *args, **kwargs)
    
    #Enqueue and clear out ready delayed jobs.
    def enqueue_delayed_jobs(self):
        now = int(time.mktime(time.gmtime()))
        
        #fetch delayed jobs and delete in one operation
        pipe = self.redis.pipeline(transaction=True)
        pipe.zrangebyscore('queue:delayed', 0, now)
        pipe.zremrangebyscore('queue:delayed', 0, now)
        res = pipe.execute()
        
        jobs = res[0]
        
        for pickled_job in jobs:
            job_data = pickle.loads(pickled_job)
            
            self._add_to_queue(job_data['job'], job_data['queue'], *job_data['args'], **job_data['kwargs'])
         
        #no need already removed   
        #self.redis.zrem('queue:delayed', pickled_job)

        return len(jobs)
    
    def _add_to_queue(self, job, queue_name, *args, **kwargs):
        return Queue(
                queue_name, 
                connection=self.redis
            ).enqueue(job, *args, **kwargs)
    