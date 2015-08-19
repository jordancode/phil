from framework.utils.id import Id
from framework.config.config import Config
import random
import mysql.connector

class MySQLShard:
    
    _shard_id = None
    _pool = None
    _config = None
    _connection = None
    _cursor = None
    
    _in_transaction = False
            
            
    def __init__(self, shard_id, config, pool):
        self._shard_id = shard_id
        self._config = config
        self._pool = pool
    
    def _get_connection(self):
        if self._connection is None:
            self._connect()
        
        return self._connection
        
    def _connect(self, side_num = None):
        if self._connection is None:
            server_config = self.get_server(side_num)
            self._connection = mysql.connector.connect(
                                    user=Config.get("mysql","user"), 
                                    password=Config.get("mysql","pass"),
                                    database=self.get_name(),
                                    host = server_config["host"],
                                    port = server_config["port"]
                                    )
            
            self._connection.autocommit = True    
    
    
    def query(self, query, params = None, use_multi = False):
        cursor = self._get_cursor()
        
        results = cursor.execute(query, params, multi=use_multi)
        ret = []
        
        if use_multi:
            for res in results:
                ret.append(self._get_result_from_cursor(res))
        else:
            ret = self._get_result_from_cursor(cursor)
            
        if not self._in_transaction:
            self._close_cursor()
        
        return ret
    
    def _get_result_from_cursor(self,cursor):
        ret = None
        
        if cursor.with_rows:
            ret = cursor.fetchall()
        else:
            ret = cursor.rowcount
            
        return ret
    
    def multi_query(self,query, params_arr=None):
        cursor = self._get_cursor()
        
        ret = []
        
        cursor.executemany(query, params_arr)
        
        if cursor.with_rows:
            ret.append(cursor.fetchall())
        else:
            ret.append(cursor.rowcount)
         
        if not self._in_transaction:
            self._close_cursor()       
        
        return ret
    
    
    def get_server(self,side_num = None):
        
        side_list = self._config["servers"]
        
        if side_num is None:
            """
                if we have more than one side for this shard, pick a random one and connect to that,
                future calls from this thread will use this connection as well
            """   
            side_num = random.randrange(0,len(side_list))
        
        return side_list[side_num]
                                 
    
    def get_pool(self):
        return self._pool    
        
    
    def get_name(self):
        return self._pool.get_name() + "_" + str(self._shard_id)
    
    def start_transaction(self):
        if not self._in_transaction:
            self._get_connection().start_transaction()
            self._open_transaction()
            
    def commit(self):
        if self._in_transaction:
            self._get_connection().commit()
            self._close_transaction()
        
    
    def rollback(self):
        if self._in_transaction:
            self._get_connection().rollback()
            self._close_transaction()
    
    def close(self):
        self._close_transaction()
        if self._connection is not None:
            self._connection.close()
            self._connection = None
    
    
    def _open_transaction(self):
        self._get_connection().autocommit = False
        self._in_transaction = True
            
        
    def _close_transaction(self):
        self._close_cursor()
        self._get_connection().autocommit = True
        self._in_transaction = False
        
    def _get_cursor(self):
        if self._cursor is None:
            self._cursor = self._get_connection().cursor(dictionary=True)
        return self._cursor
            
    def _close_cursor(self):
        if self._cursor is not None:
            self._cursor.close()
            self._cursor = None
        
        
        