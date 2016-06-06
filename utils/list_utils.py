class ListUtils:
    
    
    @staticmethod
    def dedupe(list_):
        #keep a hash of what we've seen, skip if in it
        h = {  }
        cpy = []
        for el in list_:
            if el in h:
                continue
            h[el] = True
            cpy.append(el)
            
        return cpy
    
    @staticmethod
    def to_human_string(list_):
        if not len(list_):
            return ""
        
        last_el = list_.pop(-1)
        previous_els = ", ".join(list_)
        
        if previous_els:
            return previous_els + " and " + last_el
            
        return last_el
        
    
    @staticmethod
    def array_chunk(list_, chunk_size):
        #does PHP array_chunk
        return [list_[i : i + chunk_size] for i in range(0, len(list_), chunk_size)]
            