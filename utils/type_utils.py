from framework.utils.date_utils import DateUtils
import json


class TypeUtils:
    
    #types
    TYPE_INT = "int"
    TYPE_FLOAT = "float"
    TYPE_BOOL = "bool"
    TYPE_STRING = "string"
    TYPE_UNIXTIME = "unixtime"
    TYPE_JSON = "json"
    
    #suffixes to make a type an array or dict type
    ARRAY_SUFFIX = "[]"
    DICT_SUFFIX = "{}"
    
    #everything not in this list is considered False
    TRUTHY_VALUES = ["true", "True", "1", 1, True]
        
    
    @classmethod
    def coerce_type(cls, value, type):
        
        if cls.is_array_type(value):
            base_type = cls.get_base_type(type)
            return [ cls.coerce_type(v, base_type) for v in value ]
        elif cls.is_dict_type(value):
            base_type = cls.get_base_type(type)
            return { k : cls.coerce_type(v, base_type) for k,v in value.items() }
        
        
        if value is not None:
            if type == cls.TYPE_INT:
                return int(value)
            elif type == cls.TYPE_FLOAT:
                return float(value)
            elif type == cls.TYPE_STRING:
                return str(value)
            elif type == cls.TYPE_BOOL:
                return value in cls.TRUTHY_VALUES
            elif type == cls.TYPE_UNIXTIME:
                #cast to float from string then to int to remove decimal 
                ts = int(float(value))
                if ts > 0:
                    return DateUtils.unix_to_datetime(ts)
                return None
            elif type == cls.TYPE_JSON:
                return json.loads(value)
        
        #unknown type
        return value
    
    @classmethod
    def get_base_type(cls, type):
        return type[0:-2]
    
    @classmethod
    def is_array_type(cls, type):
        if type is None:
            return False
        return type[-2:] == cls.ARRAY_SUFFIX
    
    @classmethod
    def is_dict_type(cls, type):
        if type is None:
            return False
        return type[-2:] == cls.DICT_SUFFIX