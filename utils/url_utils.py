
class URLUtils:
    
    
    @staticmethod
    def get_query_string(query_params):
        param_arr=[]
        for k,v in query_params.items():
            if v is not None:
                param_arr.append(str(k)+"="+str(v))
        
        if not len(param_arr):
            return ""
        
        return "?" + "&".join(param_arr)
        
        