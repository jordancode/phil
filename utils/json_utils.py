from framework.utils.date_utils import DateUtils
import datetime
import json
class JSONUtils:
    
    _optional_keys = None
    
    @classmethod
    def dumps(cls, dict_or_array, optional_keys = None):
        
        cls._optional_keys = optional_keys
        return json.dumps(dict_or_array, sort_keys=True, default=cls._json_helper)
    
    
    @classmethod
    def _json_helper(cls, value):
        
        #stringifies otherwise non-json nodes
        try:
            return value.to_dict(True, cls._optional_keys)
        except AttributeError:
            pass
        
        
        try:
            if isinstance(value, datetime.datetime):
                return DateUtils.datetime_to_unix(value)
            
            return str(value)
        except AttributeError:
            pass
        
        raise TypeError()