from framework.storage.mysql import MySQL
from framework.storage.mysql_pool import MySQLPool
from framework.utils.id import Id
from multiprocessing.pool import Pool
from framework.utils.query_builder import SQLQueryBuilder

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
    def multi_shard_insert(cls, table_name, shard_by_col_name, dicts_to_insert, cols_to_update = None, pool = None,num_threads = None):
        if pool is None:
            pool = MySQLPool(MySQLPool.MAIN)
        elif isinstance(pool, int):
            pool = MySQLPool(pool)
            
        count = 0
            
        #construct mapping of inserted objects to shard that they go to
        shard_to_dicts = {}
        for d in dicts_to_insert:
            try:
                primary_id = d[shard_by_col_name]
                shard_id = Id(primary_id).get_shard_id()
                
                if shard_id not in shard_to_dicts:
                    shard_to_dicts[shard_id] = []
                shard_to_dicts[shard_id].append(d)
                
            except Exception as e:
                #skip objects that don't have the shard_by_col, or in wrong format
                raise e
        
        for shard_id, dict_list in shard_to_dicts.items():
            #get vals array
            vals = [ ["%s" for k in d.keys()] for d in dict_list ]
            #create parameter placeholders
            params = [ v for d in dict_list for v in d.values()]
            #get cols
            cols = dict_list[0].keys()
            
            
            qb = SQLQueryBuilder.insert(table_name).columns(cols).values(vals)
            
            if cols_to_update:
                update_list = [ ("`" + c + "`", "VALUES(`" + c+ "`)") for c in cols_to_update ]
                qb.on_duplicate_key_update(update_list)
            
            
            #do insert
            count = count + MySQL.get_by_shard_id(shard_id, pool.get_id()).query(qb.build(), params)
            
        return count
    
    
    @classmethod
    def multi_shard_query_by_shard_id(cls, shard_id_list, query, params = None, pool = None,num_threads = None):
        """
            Runs a query shards given by the provided shard_ids
        """
        
        if pool is None:
            pool = MySQLPool(MySQLPool.MAIN)
        
        run_one = cls._get_query_runner(pool, query, params ) 
        
        #with Pool(num_threads) as p:
        res = map(run_one, shard_id_list)
        
        return cls._prepare_result(res)
        
    
    @classmethod
    def multi_shard_in_list_query(cls, in_list, query, other_params = None, pool = None,num_threads = None):
        """
            Looks for a %l in the query string and replaces it with (%s, %s ...)
            It will parse the in_list parameter and run the correct list on each shard
            This is an optimized way to do a multi-shard lookup on a list of primary keys
            
            Limitations:
            - only 1 %l param can be in the query
            - %l must be the last param in the query
        
        """
        if other_params is None:
            other_params = ()
        
        if pool is None:
            pool = MySQLPool(MySQLPool.MAIN)
            
        shard_id_to_in_list = {}
        for id in in_list:
            shard_id = Id(id).get_shard_id()
            if not shard_id in shard_id_to_in_list:
                shard_id_to_in_list[shard_id] = [id]
            else:
                shard_id_to_in_list[shard_id].append(id)
        
        run_one = cls._get_in_list_query_runner(pool, query, other_params, shard_id_to_in_list) 
        
        #with Pool(num_threads) as p:
        res = map(run_one, shard_id_to_in_list.keys())
        
        
        return cls._prepare_result(res)
            
            
    @staticmethod
    def _get_in_list_query_runner(pool, query_str, other_params, shard_id_to_in_list):
        # bind pool and query string to a function
        # that can make a query per shard id  
        def run_one_query(shard_id):
            if not shard_id in shard_id_to_in_list:
                return None;
            
            in_list = shard_id_to_in_list[shard_id]
            qry = query_str.replace("%l", "( " + ", ".join(map(lambda x :"%s", in_list)) + " )",1)
            
            shard = pool.get_shard(shard_id)
            query_res = shard.query(qry, other_params + tuple(in_list))
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
        
            
            
    @staticmethod
    def _prepare_result(res):
        try:
            return sum(res, [])
        except TypeError:
            return sum(res, 0)

