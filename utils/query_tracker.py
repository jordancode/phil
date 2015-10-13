from datetime import datetime

class QueryTracker():
    
    _stack = []
    
    @classmethod
    def push(cls, shard_name, query, parameters, result):
        cls._stack.append(
            {
             "shard_name" : shard_name, 
             "query" : query, 
             "parameters" : parameters, 
             "result" : result, 
             "ts" : datetime.now()
            }
        )
        
        
    @classmethod
    def get_query_history(cls):
        return cls._stack
    