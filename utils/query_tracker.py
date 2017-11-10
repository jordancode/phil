from datetime import datetime
import logging
import pprint

class QueryTracker():
    
    """
        Debug utility for keeping track of MySQL queries made over the course of a
        web request and how long they took. 
    """
    
    
    _stack = []
    _on = False
    
    @classmethod
    def push(cls, shard_name, query, parameters, result = None, error = None):
        
        q_data ={
             "shard_name" : shard_name, 
             "query" : query, 
             "parameters" : parameters, 
             "result" : result, 
             "ts" : datetime.now()
            }
        
        if cls._on:
            cls._stack.append(q_data)
            logging.getLogger().debug(pprint.pformat(q_data))
        
        return q_data
    
    @classmethod
    def enable(cls):
        cls._on = True
    
    @classmethod
    def is_enabled(cls):
        return cls._on
        
    
    @classmethod
    def get_query_history(cls):
        return cls._stack
    
    @classmethod
    def clear(cls):
        cls._stack = []
        cls._on = False