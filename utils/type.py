from framework.utils.date_utils import DateUtils
import json
from framework.models.domain.serializeable import CircularRefException
from framework.utils.attr import Attr
import logging


class Type:
    
    #types
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STRING = "string"
    UNIXTIME = "unixtime"
    JSON = "json"
    
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
            except Exception as e:
                logging.getLogger().debug("SERIALIZATION ERROR")
                logging.exception(e)
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
        
        
        
        
        
        
        