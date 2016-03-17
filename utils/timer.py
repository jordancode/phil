import datetime
class Timer:
    
    _start_ts = None
    _elapsed_delta = None
    
    def __init__(self):
        self.start()
    
    
    def start(self):
        if not self._start_ts:
            self._start_ts = datetime.datetime.now()
    
    
    def pause(self):
        now = datetime.datetime.now()
        
        if self._start_ts:
            new_delta = now - self._start_ts
        else:
            new_delta = datetime.timedelta()
        
        if self._elapsed_delta:
            self._elapsed_delta += new_delta
        else:
            self._elapsed_delta = new_delta
        
        return self._elapsed_delta
            
    
    
    def stop(self):
        delta = self.pause()
        
        self._start_ts = None
        self._elapsed_delta = None
        
        return delta.total_seconds()