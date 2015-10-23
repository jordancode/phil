class SQLUtils:
    
    @staticmethod
    def get_limit_string(count = None, offset = None):
        sql = ""
        
        if offset is not None and count is not None:
            sql = " LIMIT " + int(offset) + "," + int(count)
        elif count is not None:
            sql = " LIMIT " + int(count)
        elif offset is not None:
            sql = " LIMIT " + int(offset) + ",999999999"
        
        return sql
        