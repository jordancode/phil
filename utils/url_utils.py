import json
import urllib.parse

class URLUtils:
    
    
    @staticmethod
    def get_query_string(query_params):
        param_arr=[]
        for k,v in query_params.items():
            if v is not None:
                if isinstance(v, dict):
                    v=json.dumps(v)
                else:
                    v=str(v)
                v=urllib.parse.quote(v)
                
                param_arr.append(str(k)+"="+v)
        
        if not len(param_arr):
            return ""
        
        return "?" + "&".join(param_arr)
        
        