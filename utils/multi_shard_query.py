from framework.storage.mysql import MySQL
from framework.storage.mysql_pool import MySQLPool
from framework.utils.id import Id
from multiprocessing.pool import Pool

class MultiShardQuery:
    
    
    @classmethod
    def all_shard_query(cls, query, params = None, pool = None, num_threads = None):
        """
            Runs a query on all shards and returns result. 
        """
        if pool is None:
            pool = MySQLPool(MySQLPool.MAIN)
        
        return cls.multi_shard_query_by_shard_id(
                range(pool.get_num_shards()), query, params, pool, num_threads
            )
    
    @classmethod
    def multi_shard_query(cls, id_list, query, params = None, pool = None,num_threads = None):
        """
            Runs a query on just the shards used for the provided id_list 
        """
        if pool is None:
            pool = MySQLPool(MySQLPool.MAIN)
        
        seen_shard_ids = {}
        for id in id_list:
            seen_shard_ids[Id(id).get_shard_id()] = True
            
        return cls.multi_shard_query_by_shard_id(
                seen_shard_ids.keys(), query, params, pool, num_threads
            )
    
    
    @classmethod
    def multi_shard_query_by_shard_id(cls, shard_id_list, query, params = None, pool = None,num_threads = None):
        """
            Runs a query shards given by the provided shard_ids
        """
        
        if pool is None:
            pool = MySQLPool(MySQLPool.MAIN)
        
            
        
        run_one_query = cls._get_query_runner(pool, query, params ) 
        
        with Pool(num_threads) as p:
            res = p.map(run_one_query, shard_id_list)
        
        return res
    
    @classmethod
    def multi_shard_in_list_query(cls, in_list, query, other_params, pool = None,num_threads = None):
        """
            Looks for a %l in the query string and replaces it with LIST(%s, %s ...)
            It will parse the in_list parameter and run the correct list on each shard
            This is an optimized way to do a multi-shard lookup on a list of primary keys
            
            Limitations:
            - only 1 %l param can be in the query
            - %l must be the last param in the query
        """
        
        if pool is None:
            pool = MySQLPool(MySQLPool.MAIN)
            
        shard_id_to_in_list = {}
        for id in in_list:
            shard_id = Id(id).get_shard_id()
            if not shard_id in shard_id_to_in_list:
                shard_id_to_in_list[shard_id] = [id]
            else:
                shard_id_to_in_list[shard_id].append(id)
        
        run_one_query = cls._get_in_list_query_runner(pool, query, other_params, shard_id_to_in_list) 
        
        with Pool(num_threads) as p:
            res = p.map(run_one_query, shard_id_to_in_list.keys())
            
        return res
            
            
    @staticmethod
    def _get_in_list_query_runner(pool, query_str, other_params, shard_id_to_in_list):
        # bind pool and query string to a function
        # that can make a query per shard id  
        def run_one_query(shard_id):
            if not shard_id in shard_id_to_in_list:
                return None;
            
            in_list = shard_id_to_in_list[shard_id]
            qry = query_str.replace("%l", "LIST(" + ", ".join(map(lambda x :"%s", in_list)) + ")",1)
            
            shard = pool.get_shard(shard_id)
            query_res = shard.query(qry, other_params + in_list)
            shard.close() 
            return query_res
        
        return run_one_query
            
            
                
    @staticmethod
    def _get_query_runner(pool, query_str, params):
        # bind pool and query string to a function
        # that can make a query per shard id  
        def run_one_query(shard_id):
            shard = pool.get_shard(shard_id)
            query_res = shard.query(query_str, params)
            shard.close() 
            return query_res
        
        return run_one_query
        
            
            
    
    

