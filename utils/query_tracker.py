from datetime import datetime

class QueryTracker():
    
    _stack = []
    
    @classmethod
    def push(cls, shard_name, query, parameters, result = None, error = None):
        q_data ={
             "shard_name" : shard_name, 
             "query" : query, 
             "parameters" : parameters, 
             "result" : result, 
             "ts" : datetime.now()
            }
        cls._stack.append(q_data)
        
        return q_data
        
        
    @classmethod
    def get_query_history(cls):
        return cls._stack
    
    @classmethod
    def clear(cls):
        cls._stack = []