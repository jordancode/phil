from abc import ABCMeta
from framework.utils.sql_utils import SQLUtils
from _ctypes import ArgumentError
from framework.utils.associative_array import SORT_HI_TO_LO, SORT_LO_TO_HI

DIRECTION_ASC = "ASC"
DIRECTION_DESC = "DESC"

LOCK_FOR_UPDATE = "FOR UPDATE"
LOCK_FOR_SHARED_STATE = "FOR SHARED_STATE"

class WhereClause(metaclass=ABCMeta):
    
    OPERATORS = [
        "=", 
        "<", 
        ">", 
        "<>",
        "<=>", 
        "!=", 
        "<=", 
        ">=",
        "BETWEEN",
        "NOT BETWEEN",
        "IS",
        "IS NOT", 
        "IN",
        "NOT IN", 
        "LIKE"]
    
    _where_nodes = None
    
    def __init__(self, node_list = None):
        self._where_nodes = []
        if node_list:
            for node in node_list:
                self.append(node)
    
    def append(self, where_node):
        if isinstance(where_node, tuple):
            if len(where_node) != 3 or where_node[1] not in self.OPERATORS:
                raise ArgumentError()
        elif not isinstance(where_node, WhereClause):
            raise ArgumentError()
        
        self._where_nodes.append(where_node)
    
    def build(self):
        glue = (" " + self._get_conjuction() + " ")
        ret = glue.join(
              self._build_node(node) for 
              node in self._where_nodes
            )
        
        return ret
    
    def _build_node(self, node):
        if isinstance(node, WhereClause):
            return node.build()
        else:
            return " ".join(str(n) for n in node)
    
    def _get_conjuction(self):
        pass

class And(WhereClause):
    def _get_conjuction(self):
        return "AND"
    
class Or(WhereClause):  
    def _get_conjuction(self):
        return "OR"




class BaseSQLQuery(metaclass=ABCMeta):
    
    _parts = None
    
    def __init__(self, table_name):
        self._parts = {
               "verb" : self._get_verb(),
               "table" : self._get_table_clause(table_name)
            }
    
    def _get_verb(self):
        return None
    
    def _get_table_clause(self, table_name):
        return table_name
    
    def _get_order(self):
        return ["verb", "table"]
    
    def _required(self):
        return ["verb", "table"]
    
    def _validate_required(self):
        for part in self._required():
            if part not in self._parts or not self._parts[part]:
                raise BadQueryError()
    
    def build(self):
        self._validate_required()
        
        string_parts = []
        for part in self._get_order():
            if part in self._parts:
                string_parts.append(self._parts[part])
        
        return " ".join(string_parts)        



class WhereQuery(BaseSQLQuery,metaclass=ABCMeta):
    def where(self, where_clause):
        if isinstance(where_clause, tuple):
            where = " ".join(str(n) for n in where_clause)
        else:
            where = where_clause.build()
        
        self._parts["where"] = "WHERE " + where
        return self
    
    def order_by(self, column, direction = None):
        assert direction in [None, DIRECTION_ASC, DIRECTION_DESC, 
                             SORT_HI_TO_LO, SORT_LO_TO_HI]
        
        
        if direction is SORT_HI_TO_LO:
            direction = DIRECTION_DESC
            
        elif direction is SORT_LO_TO_HI:
            direction = DIRECTION_ASC
            
        
        self._parts["order"] = "ORDER BY " + column
        if direction:
            self._parts["order"] += " " + direction
        return self
    
    def limit(self, count=None, offset=None):
        self._parts["limit"] = SQLUtils.get_limit_string(count, offset)
        return self
    
class IgnorableQuery(BaseSQLQuery,metaclass=ABCMeta):
    def ignore(self, boolean = True):
        if boolean:
            self._parts["ignore"] = "IGNORE"
        elif "ignore" in self._parts:
            del(self._parts["ignore"])
        return self
   

class SQLSelectQuery(WhereQuery, BaseSQLQuery):
        
    def __init__(self, table_name):
        super().__init__(table_name)
        self._parts["columns"] = "*" #use * as default for column list
        
    def columns(self, column_list):
        self._parts["columns"] = ",".join(column_list)
        return self
    
    
    def lock(self, lock_type = LOCK_FOR_UPDATE):
        assert lock_type in [LOCK_FOR_UPDATE, LOCK_FOR_SHARED_STATE]
        
        self._parts["lock"] = lock_type
        return self 
    
    def _get_table_clause(self, table_name):
        return "FROM " + table_name
    
    def _get_verb(self):
        return "SELECT"
    
    def _get_order(self):
        return ["verb", "columns", "table", "where", "order", "limit", "lock"]
    
    def _required(self):
        return ["verb", "columns", "table"]

   
class SQLInsertQuery(IgnorableQuery, BaseSQLQuery):
    def __init__(self, table_name):
        super().__init__(table_name)
            
    def columns(self, col_array):
        self._parts["table_def"] = "("+ ",".join(col_array) + ")"
        return self
    
    def values(self, values_arr):
        
        if len(values_arr):
            s = "VALUES "
            #if we are inserting multiple rows, need to collapse to strings
            if isinstance(values_arr[0], list):
                values_arr = ["(" + ",".join(v) + ")" for v in values_arr]
            
            s += ",".join(values_arr)
            
            self._parts["values"] = s
        
        return self
    
    def on_duplicate_key_update(self, col_to_value_array):
        self._parts["dupe"] = ("ON DUPLICATE KEY UPDATE " + 
            ", ".join(col + "=" + val for (col,val) in col_to_value_array))
        return self
    
    def select(self, select_query_string):
        self._parts["values"] = select_query_string
        return self
        
    def _get_table_clause(self, table_name):
        return "INTO " + table_name
    
    def _get_verb(self):
        return "INSERT"
    
    def _get_order(self):
        return ["verb", "ignore", "table", "table_def", "values", "dupe"]
    
    def _required(self):
        return ["verb", "table", "values" ]


class SQLUpdateQuery(WhereQuery,IgnorableQuery,BaseSQLQuery):
    def __init__(self, table_name):
        super().__init__(table_name)
    
    def set(self, col_to_value_array):
        self._parts["set"] = ("SET " + 
            ", ".join(col + "=" + val for (col,val) in col_to_value_array))
        return self
    
    
    def _get_verb(self):
        return "UPDATE"
    
    def _get_table_clause(self, table_name):
        return table_name
    
    def _get_order(self):
        return ["verb", "ignore", "table", "set", "where", "order", "limit"]
    
    def _required(self):
        return ["verb", "table", "set" ]


class SQLDeleteQuery(WhereQuery,IgnorableQuery,BaseSQLQuery):
    
    def __init__(self, table_name):
        super().__init__(table_name)
    
    def _get_verb(self):
        return "DELETE"
    
    def _get_table_clause(self, table_name):
        return "FROM " + table_name
    
    def _get_order(self):
        return ["verb", "ignore", "table", "where", "order", "limit"]
    
    def _required(self):
        return ["verb", "table"]

class BadQueryError(Exception):
    def __init__(self):
        super().__init__("Query could not be built")


class SQLQueryBuilder:
    
    @staticmethod
    def select(table_name) -> SQLSelectQuery:
        return SQLSelectQuery(table_name)
    
    @staticmethod
    def insert(table_name) -> SQLInsertQuery:
        return SQLInsertQuery(table_name)
    
    @staticmethod
    def update(table_name) -> SQLUpdateQuery:
        return SQLUpdateQuery(table_name)
    
    @staticmethod
    def delete(table_name) -> SQLDeleteQuery:
        return SQLDeleteQuery(table_name)