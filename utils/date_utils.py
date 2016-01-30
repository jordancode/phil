from datetime import datetime
import time

class DateUtils:
    
    @staticmethod
    def mysql_to_datetime(mysql_time_string = None):
        if mysql_time_string is None:
            return datetime.now()
        
        return datetime.strptime(mysql_time_string, "%Y-%M-%D %H:%M:%S")
    
    @staticmethod
    def datetime_to_mysql(dt = None):
        if dt is None:
            return str(dt.now())
        
        return str(dt)
    
    @staticmethod
    def mysql_to_unix(mysql_time_string = None):
        dt = DateUtils.mysql_to_datetime(mysql_time_string)
        return DateUtils.datetime_to_unix(dt)
    
    @staticmethod
    def unix_to_datetime(ts_seconds = None):
        if ts_seconds is None:
            return datetime.now()
        
        return datetime.fromtimestamp(ts_seconds)
    
    @staticmethod
    def unix_to_mysql(ts_seconds = None):
        dt = DateUtils.unix_to_datetime(ts_seconds)
        return DateUtils.datetime_to_mysql(dt)


    @staticmethod
    def fb_to_datetime(fb_time):
        fb_time = fb_time[:fb_time.rindex("+")]
        return datetime.strptime(fb_time, '%Y-%m-%dT%H:%M:%S')


    @staticmethod
    def datetime_to_unix(dt = None):
        if dt is None:
            dt = datetime.now()
        
        return int(time.mktime(dt.timetuple()))

    @staticmethod
    def sort_index_from_date(parent_id, dt = None):
        if dt is None:
            dt = datetime.now()
        
        return SortIndex.get_for_date(parent_id, dt).get_value()


from framework.models.domain.sort_index import SortIndex