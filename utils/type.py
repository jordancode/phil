import datetime
import json
import logging

from framework.models.serializeable import CircularRefException
from framework.utils.attr import Attr
from framework.utils.date_utils import DateUtils


class Type:
    
    """
        
    """
    
    #types
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STRING = "string"
    ASCII = "ascii" #a string restricted to the ascii characters
    UNIXTIME = "unixtime"
    JSON = "json"
    BYTES = "bytes"
    
    #suffixes to make a type an array or dict type
    ARRAY_SUFFIX = "[]"
    DICT_SUFFIX = "{}"
    
    #everything not in this list is considered False
    TRUTHY_VALUES = ["true", "True", "1", 1, True]
        
    
    @classmethod
    def coerce_type(cls, value, dest_type):
        
        if value is not None:
            
            if cls.is_array_type(dest_type):
                base_type = cls.get_base_type(dest_type)
                return [ cls.coerce_type(v, base_type) for v in value ]
            elif cls.is_dict_type(dest_type):
                base_type = cls.get_base_type(dest_type)
                return { k : cls.coerce_type(v, base_type) for k,v in value.items() }
            
            
            if dest_type == cls.INT:
                return int(value)
            elif dest_type == cls.FLOAT:
                return float(value)
            elif dest_type == cls.STRING:
                if isinstance(value, bytes):
                    value = value.decode("utf-8")
                return str(value)
            elif dest_type == cls.ASCII:
                if isinstance(value, str):
                    value = value.encode("ascii","ignore")
                return value.decode("ascii","ignore")
                
            elif dest_type == cls.BOOL:
                return value in cls.TRUTHY_VALUES
            elif dest_type == cls.UNIXTIME:
                if isinstance(value, datetime.datetime):
                    return value
                
                #cast to float from string then to int to remove decimal
                try: 
                    ts = int(float(value))
                    if ts > 0:
                        return DateUtils.unix_to_datetime(ts)
                except (ValueError, TypeError):
                    pass
                try:
                    return DateUtils.mysql_to_datetime(value)
                except (ValueError, TypeError):
                    pass
                
                return None
            elif dest_type == cls.JSON:
                return json.loads(value)
        
        #unknown type
        return value
    
    @classmethod
    def get_base_type(cls, dest_type):
        return dest_type[0:-2]
    
    @classmethod
    def is_array_type(cls, dest_type):
        if dest_type is None or not isinstance(dest_type,str):
            return False
        return dest_type[-2:] == cls.ARRAY_SUFFIX
    
    @classmethod
    def is_dict_type(cls, dest_type):
        if dest_type is None or not isinstance(dest_type,str):
            return False
        return dest_type[-2:] == cls.DICT_SUFFIX
    
    @classmethod
    def serialize(cls, obj_, optional_keys=None):
        return cls._recursive_serialize_type(obj_, [], optional_keys)
        
    @classmethod
    def _recursive_serialize_type(cls, obj_, seen_refs, optional_keys=None):
        
        #handles the different objects that could be in the type array and 
        if isinstance(obj_, type):
            #if obj_ in seen_refs:
                #raise CircularRefException()
            seen_refs.append(obj_)
            
            try:
                d = obj_.get_definition_for_keys(optional_keys)
                d["object"]= obj_.__name__
                
                return cls._recursive_serialize_type(d, seen_refs, optional_keys)
            except CircularRefException:
                logging.getLogger().debug("CIRCULAR REFERENCE")
                return obj_.__name__
            except Exception:
                return obj_.__name__
            
        elif isinstance(obj_, Attr):
            return cls._recursive_serialize_type(obj_.get_type(), seen_refs, optional_keys)
        elif isinstance(obj_, list):
            return [ 
                cls._recursive_serialize_type(t, seen_refs, optional_keys ) 
                for t in obj_
            ]
        elif isinstance(obj_, dict):
            return { 
                k : cls._recursive_serialize_type(t, seen_refs, optional_keys ) 
                for k, t in obj_.items()
            }
        else:
            return str(obj_)
        
        
        
        
        
        
        