
class Attr:
    
    _type = None
    _lazy = None
    _required = False
    
    def __init__(self, type, lazy=None, required=None, required_for_api=None):
        self._type = type
        self._lazy = lazy
        
        #by default, lazy attributes are not required, everything else is
        if required is None:
            self._required = self._lazy is None
        else:
            self._required = required
        
        self._required_for_api=required_for_api
    
    def get_type(self):
        return self._type
    
    def is_required(self):
        return self._required
    
    def is_required_for_api(self):
        return self._required_for_api
    
    def is_lazy(self):
        return self._lazy is not None
    
    def get_lazy_value(self, ins):
        if not self.is_lazy():
            return None
        
        return self._lazy(ins)