import hashlib
import random

from framework.utils.id import Id, BadIdError
import logging
from framework.config.config import Config
import mysql.connector
from framework.utils.query_tracker import QueryTracker
import pprint


class MySQL:
    
    _pools = None
    _conn_mgr = None
    
    
    @classmethod
    def get_shard_id_for_string(cls, string, pool_id = None):
        if pool_id is None:
            pool_id = MySQLPool.MAIN
            
        pool = cls.get_pool(pool_id)
        
        #use python built-in hash for this
        md5 = int(hashlib.md5(string.encode("utf-8")).hexdigest(),16) 
        
        
        return md5 % pool.get_num_shards()
    
    @classmethod
    def get(cls, id):
        if not isinstance(id,Id):
            id = Id(id) 
         
        shard = id.get_shard_id()
        pool_id = id.get_pool_id()
        
        pool = cls.get_pool(pool_id)
        
        return pool.get_shard(shard) 
    
    @classmethod
    def get_by_shard_id(cls, shard_id, pool_id = None):
        if pool_id is None:
            pool_id = MySQLPool.MAIN
        
        pool = cls.get_pool(pool_id)
        
        return pool.get_shard(shard_id)
    
    @classmethod
    def get_pool(cls,pool_id):
        if cls._pools is None:
            cls._pools = {}
        
        if not pool_id in cls._pools:
            cls._pools[pool_id] = MySQLPool(pool_id)
            
        return cls._pools[pool_id]
    
    @classmethod
    def next_id_like(cls, entity_id, pool_id = None):
        if not isinstance(entity_id, Id):
            entity_id = Id(entity_id)
        
        return MySQL.next_id(
                entity_id.get_shard_id(), 
                pool_id or entity_id.get_pool_id()
                )
        
        
    
    @classmethod
    def next_id(cls,shard_id = None,pool_id = None, number_ids = 1):
             
        if pool_id is None:
            pool_id = MySQLPool.MAIN
        
        pool = cls.get_pool(pool_id)
        
        #pick a random shard id if one wasn't provided
        if shard_id is None:
            shard_id = random.randrange(0, pool.get_num_shards())
        
        return Id.next(shard_id, pool_id, number_ids)
    
    @classmethod
    def get_conn_mgr(cls):
        if cls._conn_mgr is None:
            cls._conn_mgr = MySQLConnectionManager(Config.get("mysql"))
            
        return cls._conn_mgr 
    
    
    @classmethod
    def close_all(cls):
        if cls._conn_mgr:
            cls._conn_mgr.close_all()
        cls._conn_mgr = None


    

    @classmethod     
    def get_transaction(cls):
        return MySQLTransaction(cls.get_conn_mgr())






class MySQLPool:
    
    MAIN = 0
    
    _id = None
    _shards = None
    _config = None
    
    
    def __init__(self, pool_id = 0):
        self._id = pool_id
        self._shards = {}
        
        pool_config = Config.get("mysql","pools")
        if pool_id < 0 or pool_id >=  len(pool_config):
            raise PoolIdOutOfRangeError(pool_id)
        
        self._config = pool_config[str(pool_id)]  
        
        
    def get_shard(self, shard_id):
        if not shard_id in self._shards:
            self._shards[shard_id] = MySQLShard(shard_id, self)
            
        return self._shards[shard_id]
        
    
    def get_id(self):
        return self._id
    
    
    def get_name(self):
        return self._config["name"]
    
    
    def get_num_shards(self):
        return self._config["num_virt_shards"]
    
  
    
    def get_config_for_shard(self, shard_id):
        box_list = self._config["phys_shards"]
        for box_config in box_list:
            if shard_id >= box_config['min_virt_shard'] and shard_id <= box_config['max_virt_shard']:
                return box_config
        
        raise ShardIdOutOfRangeError(shard_id)
       




class MySQLShard:
    
    _shard_id = None
    _pool = None
    _side_num = None
    
            
    def __init__(self, shard_id, pool, side_num = None):
        self._shard_id = shard_id
        self._pool = pool
        self._side_num = side_num
    
    def _get_connection(self):
        return MySQL.get_conn_mgr().get_connection(self._get_host(), self._get_port())
    
    def _has_connection(self):
        return MySQL.get_conn_mgr().get_connection(self._get_host(), self._get_port())
    
    def _get_side_num(self):
        config = self._pool.get_config_for_shard(self._shard_id)
        
        if self._side_num is None:
            self._side_num = random.randrange(len(config["servers"]))
            
        self._side_num = self._side_num % len(config["servers"])
        
        return self._side_num 
    
    
    def _get_host(self):
        side_num = self._get_side_num()
        config = self._pool.get_config_for_shard(self._shard_id)
        
        return config["servers"][side_num]["host"]
            
    
    def _get_port(self):
        side_num = self._get_side_num()
        config = self._pool.get_config_for_shard(self._shard_id)
        
        return config["servers"][side_num]["port"]
    
    
    def query(self, query, params = None, use_multi = False):
        query_obj = {}
        try:
            cursor = self._get_cursor()
            
            query_obj = QueryTracker.push(self.get_name(), query, params)
            
            #use the right shard always
            cursor.execute("use " + self.get_name() + "");
            
            results = cursor.execute(query, params, multi=use_multi)
            ret = []
            
            if use_multi:
                for res in results:
                    ret.append(self._get_result_from_cursor(res))
            else:
                ret = self._get_result_from_cursor(cursor)
            
            
            warnings = cursor.fetchwarnings()
            if warnings:
                for w in warnings:
                    logging.getLogger().warn("MySQL warning: " + repr(w))
            
            query_obj["result"] = ret
            
            cursor.close()
            
        except Exception as e:
            query_obj["error"] = repr(e)
            logging.getLogger().error("MySQL error: " + repr(e))
            raise e
        
        return ret
    
    
    def _get_result_from_cursor(self,cursor):
        ret = None
        
        if cursor.with_rows:
            ret = cursor.fetchall()
        else:
            ret = cursor.rowcount
            
        return ret
    
    
    def multi_query(self,query, params_arr=None):
        
        ret = []
        cursor = self._get_cursor()
        
        cursor.executemany(query, params_arr)
        
        if cursor.with_rows:
            ret.append(cursor.fetchall())
        else:
            ret.append(cursor.rowcount)  
            
        cursor.close()  
        
        return ret                             

    
    def get_pool(self):
        return self._pool    
        
    
    def get_name(self):
        return self._pool.get_name() + "_" + str(self._shard_id)

        
    def _get_cursor(self):
        return self._get_connection().cursor(dictionary=True)






class MySQLConnectionManager:
    
    _conns = None
    _config = None
    _stoc = False
    
    def __init__(self, config):
        self._config = config
        

    def _get_server_key(self, host, port):
        return host + ":" + str(port)
    

    def get_connection(self, host, port):
        if self._conns is None:
            self._conns = {}
        
        key = self._get_server_key(host, port)
        if not key in self._conns:
            conn = self._connect(host, port)
            self._conns[key] = conn
        
        return self._conns[key]

    def has_connection(self, host, port): 
        key = self._get_server_key(host, port)
        return self._conns is not None and key in self._conns
    
    def _connect(self, host, port):
        conn = mysql.connector.connect(
                user=self._config["user"], 
                password=self._config["pass"],
                host = host,
                port = port
            )
        
        if self.start_transaction_on_connect:
            conn.start_transaction()
            conn.autocommit = False
        else:
            conn.autocommit = True
        
        return conn
    
    def close(self, host, port ):
        if not self.has_connection(host,port):
            return
        
        key = self._get_server_key(host, port)
        conn = self._conns[key] 
        del(self._conns[key])
        conn.close()
        
    
    def close_all(self):
        logging.getLogger().warn("----------------------------------------------- CLOSE ALL")
        
        if self._conns is None:
            return
        
        tmp = self._conns
        self._conns = None
        
        for key, conn in tmp.items():
            logging.getLogger().warn("Close Connection: " + key)
            if conn.in_transaction:
                logging.getLogger().warn("FORCE COMMIT: " + key)
                conn.commit()
            conn.close()
        tmp.clear()

    
    def start_transaction(self):
        logging.getLogger().warn("----- START TRANSACTION -----")
        self.start_transaction_on_connect = True
        
        if self._conns is not None:
            for conn in self._conns.values():
                if not conn.in_transaction: 
                    conn.start_transaction()
            
    
    def commit(self):
        logging.getLogger().warn("----- COMMIT -----")
        self.start_transaction_on_connect = False
        
        if self._conns is not None:
            for conn in self._conns.values():
                if conn.in_transaction:
                    conn.commit()
    
    
    def rollback(self):
        logging.getLogger().warn("----- ROLLBACK -----")
        if self._conns is not None:
            
            self.start_transaction_on_connect = False
            for conn in self._conns.values():
                if conn.in_transaction:
                    conn.rollback()
                    
    @property
    def start_transaction_on_connect(self):
        return self._stoc
    
    
    
    @start_transaction_on_connect.setter
    def start_transaction_on_connect(self, boolean):
        self._stoc = boolean



class MySQLTransaction:
    
    _conn_mgr = None
    
    def __init__(self, conn_mgr = None):
        if conn_mgr is None:
            conn_mgr = MySQL.get_conn_mgr()
        
        self._conn_mgr = conn_mgr
        
    def __enter__(self):
        self._conn_mgr.start_transaction()
    
    def __exit__(self, exception_type = None, exception = None, traceback = None):
        if exception_type is None and exception is None and traceback is None:
            self._conn_mgr.commit()
        else:
            self._conn_mgr.rollback()
        
        return False



class ShardIdOutOfRangeError(BadIdError):    
    def __init__(self, id):
        super().__init__("Shard id " + str(id) + " is out of range")
    
class PoolIdOutOfRangeError(BadIdError):
    def __init__(self, id ):
        super().__init__("Pool id " + str(id) + " is out of range") 
