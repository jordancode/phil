import pickle
import time
import uuid

import datetime
from rq import Queue

class RedisDelay(object):

    def __init__(self, redis):
        self.redis = redis

    #Delay rq job by seconds
    def delay(self, queue, seconds, job, *args, **kwargs):
        self.redis.zadd('queue:delayed',  int(time.mktime(time.gmtime())) + seconds, pickle.dumps({'job': job, 'queue': queue, 'args': args, 'kwargs': kwargs, 'id': uuid.uuid1().hex}))

    #delay a rq job to run at a datetime
    def date(self, queue, date, job, *args, **kwargs):
        sec = (date-datetime.datetime.now()).total_seconds()
        if sec < 0:
            raise Exception('Cannot schedule in past')

        return self.delay(queue, sec, job, *args, **kwargs)


    #Enqueue and clear out ready delayed jobs.
    def enqueue_delayed_jobs(self):
        jobs = self.redis.zrangebyscore('queue:delayed', 0, int(time.mktime(time.gmtime())) )

        for pickled_job in jobs:
            job = pickle.loads(pickled_job)
            Queue(job['queue'], connection=self.redis).enqueue(job['job'], *job['args'], **job['kwargs'])
            self.redis.zrem('queue:delayed', pickled_job)

        return len(jobs)