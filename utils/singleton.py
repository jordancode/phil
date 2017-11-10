class Singleton(type):
    
    """
        Meta-class for singletons. Allows a class to only be instantiated once.
        A second instantiations returns the original instance.
        
        
        usage:
        
        class MyClass(metaclass=Singleton):
            
    """
    
    _instances = {}
    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]
    
    @classmethod
    def clear_instances(cls):
        cls._instances.clear()
        