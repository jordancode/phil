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