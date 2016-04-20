from multiprocessing.pool import Pool

from framework.storage.mysql import MySQL, MySQLPool
from framework.utils.id import Id
from framework.utils.query_builder import SQLQueryBuilder


class MultiShardQuery:
    _DEFAULT_NUM_THREADS = 1
    
    def __init__(self, pool = None, num_threads = None, use_multi = False, catch_errors = False):
        if pool is None:
            pool = MySQLPool(MySQLPool.MAIN)
        elif isinstance(pool, int):
            pool = MySQLPool(pool)
        self._pool = pool
        
        if not num_threads:
            num_threads = self._DEFAULT_NUM_THREADS
            
        self._num_threads = int(num_threads)
        
        self._use_multi = bool(use_multi)
        self._catch_errors = bool(catch_errors)

        
    
    def all_shard_query(self, query, params = None):
        """
            Runs a query on all shards and returns result. 
        """
        
        return self.multi_shard_query_by_shard_id(
                range(self._pool.get_num_shards()), query, params
            )
    

    def multi_shard_query(self, id_list, query, params = None):
        """
            Runs a query on just the shards used for the provided id_list 
        """
        
        seen_shard_ids = {}
        for id in id_list:
            seen_shard_ids[Id(id).get_shard_id()] = True
            
        return self.multi_shard_query_by_shard_id(
                seen_shard_ids.keys(), query, params
            )
    
    
    def multi_shard_insert(self, table_name, shard_by_col_name, dicts_to_insert, cols_to_update = None):            
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
                if not self._catch_errors:
                    raise e
        
        for shard_id, dict_list in shard_to_dicts.items():
            
            #make sure we only have a separate call for each column set 
            dict_lists_by_cols = {}
            
            for d in dict_list:
                cols = list(d.keys())
                cols.sort()
                col_str = ",".join(cols)
                if not col_str in dict_lists_by_cols:
                    dict_lists_by_cols[col_str] = []
                dict_lists_by_cols[col_str].append(d)
            
            for col_str, dict_list in dict_lists_by_cols.items():
                #get vals array
                vals = [ ["%s" for k in d.keys()] for d in dict_list ]
                
                #create parameter placeholders
                params = [ v for d in dict_list for v in d.values()]
                cols = dict_list[0].keys()
                
                
                qb = SQLQueryBuilder.insert(table_name).columns(cols).values(vals)
                
                if cols_to_update:
                    update_list = [ ("`" + c + "`", "VALUES(`" + c+ "`)") for c in cols_to_update ]
                    qb.on_duplicate_key_update(update_list)
                
                
                #do insert
                shard = MySQL.get_by_shard_id(shard_id, self._pool.get_id())
                try:
                    count = count + shard.query(qb.build(), params, self._use_multi)
                except Exception as e:
                    if not self._catch_errors:
                        raise e
                    count = 0
            
        return count
    
    
    def multi_shard_query_by_shard_id(self, shard_id_list, query, params = None):
        """
            Runs a query shards given by the provided shard_ids
        """
        qr = QueryRunner(self._pool, query, params, self._use_multi, self._catch_errors) 
        
        
        if self._num_threads <= 1:
            res = [qr.run_one_query(i) for i in shard_id_list]
        else:
            with Pool(self._num_threads) as p:
                res = p.map(qr.run_one_query, shard_id_list)
        
        return self._prepare_result(res)
        
    
    def multi_shard_in_list_query(self, in_list, query, other_params = None):
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
            
        shard_id_to_in_list = {}
        for id in in_list:
            shard_id = Id(id).get_shard_id()
            if not shard_id in shard_id_to_in_list:
                shard_id_to_in_list[shard_id] = [id]
            else:
                shard_id_to_in_list[shard_id].append(id)
        
        qr = InListQueryRunner(self._pool, query, other_params, shard_id_to_in_list, self._use_multi, self._catch_errors) 
        
        if self._num_threads <= 1:
            res = [qr.run_one_query(i) for i in shard_id_to_in_list.keys()]
        else:
            with Pool(self._num_threads) as p:
                res = p.map(qr.run_one_query, shard_id_to_in_list.keys())
        
        
        return self._prepare_result(res)
            
    def _prepare_result(self, res):
        try:
            return sum(res, [])
        except TypeError:
            return sum(res, 0)



class BaseQueryRunner():
    
    def __init__(self, pool, query_str, use_multi, catch_errors ):
        self.pool = pool
        self.query_str = query_str
        self.use_multi = use_multi
        self.catch_errors = catch_errors
    
    def run_one_query(self, shard_id):
        #abstract
        pass
    
class QueryRunner(BaseQueryRunner):
    
    def __init__(self, pool, query_str, params, use_multi, catch_errors):
        self.params = params
        super().__init__(pool, query_str, use_multi, catch_errors)
        
    def run_one_query(self,shard_id):
        shard = self.pool.get_shard(shard_id)
        try:
            query_res = shard.query(self.query_str, self.params, self.use_multi)
        except Exception as e:
            if not self.catch_errors:
                raise e
            query_res = []
             
        return query_res
        
class InListQueryRunner(BaseQueryRunner):
    
    def __init__(self,  pool, query_str, other_params, shard_id_to_in_list, use_multi, catch_errors):
        self.other_params = other_params
        self.shard_id_to_in_list = shard_id_to_in_list
        
        super().__init__(pool, query_str, use_multi, catch_errors)
        
    def run_one_query(self,shard_id):
        if not shard_id in self.shard_id_to_in_list:
            return []
        
        in_list = self.shard_id_to_in_list[shard_id]
        qry = self.query_str.replace("%l", "( " + ", ".join(map(lambda x :"%s", in_list)) + " )",1)
        
        shard = self.pool.get_shard(shard_id)
        try:
            query_res = shard.query(qry, self.other_params + tuple(in_list), self.use_multi)
        except Exception as e:
            if not self.catch_errors:
                raise e
            query_res = []
             
        return query_res