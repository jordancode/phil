from framework.utils.date_utils import DateUtils
import datetime
import json
class JSONUtils:
    
    @classmethod
    def dumps(cls, dict_or_array, optional_keys = None, context=None, stringify_remainder=True):
        
        
        def json_helper(value):
            #stringifies otherwise non-json nodes
            try:
                value.set_context(context)
                return value.to_dict(True, optional_keys, for_api=True)
            except AttributeError:
                pass
            
            try:
                if isinstance(value, datetime.datetime):
                    return DateUtils.datetime_to_unix(value)
                
                if stringify_remainder:
                    return str(value)
            except AttributeError:
                pass
            
            raise TypeError()

        
        
        return json.dumps(dict_or_array, sort_keys=True, default=json_helper)
    
    
