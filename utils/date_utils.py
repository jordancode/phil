from datetime import datetime

class DateUtils:
    
    @staticmethod
    def mysql_to_datetime(mysql_time_string):
        return datetime.strptime(mysql_time_string, "%Y-%M-%D %H:%M:%S")
    
    @staticmethod
    def datetime_to_mysql(dt):
        return str(datetime)
    
    @staticmethod
    def mysql_to_unix(mysql_time_string):
        dt = DateUtils.mysql_to_datetime(mysql_time_string)
        return DateUtils.datetime_to_unix(dt)
    
    @staticmethod
    def unix_to_datetime(ts_seconds):
        return datetime.utcfromtimestamp(ts_seconds)
    
    @staticmethod
    def unix_to_mysql(ts_seconds):
        dt = DateUtils.unix_to_datetime(ts_seconds)
        return DateUtils.datetime_to_mysql(dt)
    
   
    @staticmethod
    def datetime_to_unix(dt):
        return dt.time()