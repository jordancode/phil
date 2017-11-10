import hashlib
import random

from framework.utils.id import Id, BadIdError
import logging
from framework.config.config import Config
import mysql.connector
from framework.utils.query_tracker import QueryTracker
from mysql.connector.errors import DatabaseError
from setuptools.ssl_support import is_available
from mysql.connector.pooling import CONNECTION_POOL_LOCK


class MySQL:
    """
        This defines a multi-sharded framework for MySQL.
        Sharding rules are defined in the Id class.
        
        mysql.config defines the mapping between virtual and physical shards
        and pool groupings.
        
        A pool is a vertical partition
        A shard is a horizontal partition
        
        pools have shards
        
        shard_id is an int between 0 and num_shards
        pool_id is an int betweeen 0 and num_pools
    """
    
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
        return MySQL.get_conn_mgr().get_connection(self._get_host(), self._get_port(), self.get_name())
    
    def _return_connection(self, conn):
        MySQL.get_conn_mgr().return_connection(conn)
    
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
        
        query_obj = QueryTracker.push(self.get_name(), query, params)
        connection=None
        
        try:
            connection = self._get_connection()
            cursor = connection.cursor(dictionary=True)
        except Exception as e:
            if connection:
                self._return_connection(connection)
                
            query_obj["error"] = repr(e)
            logging.getLogger().error("MySQL error: " + repr(e))
            raise e
        
        
        try:
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
            
        except Exception as e:
            query_obj["error"] = repr(e)
            logging.getLogger().error("MySQL error: " + repr(e))
            raise e
        
        finally:
            cursor.close()
            if connection:
                self._return_connection(connection)
        
        
        return ret
    
    
    def _get_result_from_cursor(self,cursor):
        ret = None
        
        if cursor.with_rows:
            ret = cursor.fetchall()
        else:
            ret = cursor.rowcount
            
        return ret                       

    
    def get_pool(self):
        return self._pool
        
    
    def get_name(self):
        return self._pool.get_name() + "_" + str(self._shard_id)






class MySQLConnectionManager:
    
    _conn_pools = None
    _config = None
    start_transaction_on_connect = False
    _transaction_level=0
    
    def __init__(self, config):
        self._config = config

    def get_connection(self, host, port, shard_name):
        with CONNECTION_POOL_LOCK:
            conn_pool = self.get_pool(host, port)
            
            conn = conn_pool.get_connection(shard_name)
            self._update_transaction_state(conn)
            
            return conn
        
    def return_connection(self, conn):
        with CONNECTION_POOL_LOCK:
            pool = self.get_pool(conn.server_host, conn.server_port)
            pool.return_connection(conn)
            return True

    def has_connection(self, host, port):
        with CONNECTION_POOL_LOCK: 
            key = self._get_server_key(host, port)
            return self._conn_pools is not None and key in self._conn_pools
    
    
    def get_pool(self, host, port):
        with CONNECTION_POOL_LOCK:
            if self._conn_pools is None:
                self._conn_pools = {}
            
            key = self._get_server_key(host, port)
            
            if not key in self._conn_pools:
                self._conn_pools[key] = MySQLConnectionPool(host, port, self._config)
                
            return self._conn_pools[key]
        
    
    def close(self, host, port ):
        with CONNECTION_POOL_LOCK:
            pool = self.get_pool(host, port)
            pool.close_all()
        
    
    def close_all(self):
        with CONNECTION_POOL_LOCK:
            logging.getLogger().warn("----------------------------------------------- CLOSE ALL")
            
            if self._conn_pools is None:
                return
            
            tmp = self._conn_pools
            self._conn_pools = None
            
            for key, pool in tmp.items():
                pool.close_all()
                logging.getLogger().warn("Close Connection: " + key)
                
            tmp.clear()

    
    def start_transaction(self):
        self.start_transaction_on_connect = True
        
        if self._transaction_level == 0:
            logging.getLogger().warn("----- START TRANSACTION -----")
        
        self._incr_transaction_level()
            
    
    def commit(self):
        with CONNECTION_POOL_LOCK:
            self.start_transaction_on_connect = False
            self._decr_transaction_level()
            
            if self._transaction_level <= 0:
                logging.getLogger().warn("----- COMMIT -----")
                
                if self._conn_pools is not None:
                    for conn in self.get_all_connections():
                        if conn.in_transaction:
                            conn.commit()
                            conn.autocommit = True
    
    
    def rollback(self):
        with CONNECTION_POOL_LOCK:
            self.start_transaction_on_connect = False
            
            self._decr_transaction_level()
            
            if self._transaction_level <= 0:
                logging.getLogger().warn("----- ROLLBACK -----")
            
                if self._conn_pools is not None:
                    for conn in self.get_all_connections():
                        if conn.in_transaction:
                            conn.rollback()
                            conn.autocommit = True
    
    
    def _incr_transaction_level(self):
        self._transaction_level = max(self._transaction_level + 1, 1)
    
    def _decr_transaction_level(self):
        self._transaction_level = max(self._transaction_level - 1,0)
    
    
    def get_all_connections(self):
        with CONNECTION_POOL_LOCK:
            ret = []
            if not self._conn_pools:
                return ret
            
            for pool in self._conn_pools.values():
                ret = ret + pool.get_all_connections()
            return ret
            

    def _get_server_key(self, host, port):
        return host + ":" + str(port)
    
    
    def _update_transaction_state(self, conn):
        if self.start_transaction_on_connect:
            if not conn.in_transaction: 
                conn.start_transaction()
                conn.autocommit = False
        else:
            conn.autocommit=True


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



class MySQLConnectionPool():
    
    def __init__(self, host, port, config):
        self._host = host
        self._port = port
        self._config = config
        self._max_conns = config['connections_per_host']
        self._connections = []
        
        #maps connection ids to data about the connection
        self._in_use_conns = {}
        self._current_shards = {}
        
    
    def get_connection(self, shard_name = None):
        
        is_new=False
        conn = None
        if self._has_free_connection():
            conn = self._get_free_connection(shard_name)
        else:
            if len(self._connections) >= self._max_conns: 
                raise NoMoreConnectionsException()
            conn = self._init_connection()
            is_new = True
        
        self._in_use_conns[conn.connection_id] = True
        if is_new:
            self._connections.append(conn)
        else:
            self._verify_connection(conn)
        
        if shard_name:
            self._set_shard(conn, shard_name)
        
        return conn
    
    

    
    def return_connection(self, conn):
        self._in_use_conns[conn.connection_id] = False
    
    
    def drop_connection(self, conn):
        if conn in self._connections:
            index = self._connections.index(conn)
            self._connections = self._connections[:index]+self._connections[index:]
        
        del self._in_use_conns[conn.connection_id]
        del self._current_shards[conn.connection_id]
        
    
    def get_all_connections(self):
        return self._connections
    
    def close_all(self):
        temp = self._connections
        self._connections = []
        self._in_use_conns = {}
        self._current_shards = {}
        
        for conn in temp:
            if conn.in_transaction:
                logging.getLogger().warn("FORCE COMMIT")
                conn.commit()
            conn.close()
        
    
    def _has_free_connection(self):
        for b in self._in_use_conns.values():
            if not b:
                return True
        return False    
    
    def _get_free_connection(self, shard_name = None):
        
        if shard_name:
            conn = self._get_free_connection_for_shard(shard_name)
            if conn:
                return conn        
        
        #no connection found for this shard, return any free one
        for conn_id, in_use in self._in_use_conns.items():
            if not in_use:
                return self._get_connection_by_id(conn_id)
        
        raise NoMoreConnectionsException()
    
    def _verify_connection(self, connection):
        if not connection.is_connected():
            connection.reconnect()
    
    def _get_free_connection_for_shard(self, shard_name):
        flipped_map = {}
        for conn_id, shard in self._current_shards.items():
            if shard not in flipped_map:
                flipped_map[shard] = []
            flipped_map[shard].append(conn_id)
        
            if shard_name in flipped_map:
                for conn_id_by_shard in flipped_map[shard_name]:
                    if not self._in_use_conns[conn_id_by_shard]:
                        #found an open connection already pointing to this shard!
                        return self._get_connection_by_id(conn_id_by_shard)
        
        return None
    
    
    def _get_connection_by_id(self, conn_id):
        for conn in self._connections:
            if conn.connection_id == conn_id:
                return conn
        
        return None
        
    
    def _init_connection(self):
        print(" OPEN CONNECTION TO SHARD: ")
        conn = mysql.connector.connect(
                user=self._config["user"], 
                password=self._config["pass"],
                host = self._host,
                port = self._port,
                collation = self._config.get("collation"),
                charset = self._config.get("charset"),
                )
        return conn
    
    
    def _set_shard(self, conn, shard_name):
        if( not conn.connection_id in self._current_shards 
            or self._current_shards[conn.connection_id] != shard_name ):
            conn.cmd_query("use " + shard_name)
            self._current_shards[conn.connection_id] = shard_name
        


class NoMoreConnectionsException(Exception):
    def __init__(self):
        super().__init__("No more connections, already at maximum.")


class ShardIdOutOfRangeError(BadIdError):    
    def __init__(self, id):
        super().__init__("Shard id " + str(id) + " is out of range")
    
class PoolIdOutOfRangeError(BadIdError):
    def __init__(self, id ):
        super().__init__("Pool id " + str(id) + " is out of range") 
