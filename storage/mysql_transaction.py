class MySQLTransaction:
    
    _driver = None
    
    def __init__(self, pool_or_shard):
        self._driver = pool_or_shard
        
    def __enter__(self):
        self._driver.start_transaction()
    
    def __exit__(self, exception_type = None, exception = None, traceback = None):
        if exception_type is None and exception is None and traceback is None:
            self._driver.commit()
            return False
        else:
            self._driver.rollback()
            return False