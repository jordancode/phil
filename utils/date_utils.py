import datetime
import time
from pathlib import _Accessor


class DateUtils:
    
    @staticmethod
    def mysql_to_datetime(mysql_time_string = None):
        if mysql_time_string is None:
            return datetime.datetime.now()
        
        return datetime.datetime.strptime(mysql_time_string, "%Y-%M-%D %H:%M:%S")
    
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
            return datetime.datetime.now()
        
        return datetime.datetime.fromtimestamp(ts_seconds)
    
    @staticmethod
    def unix_to_mysql(ts_seconds = None):
        dt = DateUtils.unix_to_datetime(ts_seconds)
        return DateUtils.datetime_to_mysql(dt)


    @staticmethod
    def fb_to_datetime(fb_time):
        fb_time = fb_time[:fb_time.rindex("+")]
        return datetime.datetime.strptime(fb_time, '%Y-%m-%dT%H:%M:%S')


    @staticmethod
    def google_to_datetime(g_time):
        g_time = g_time[:g_time.rindex(".")]
        return datetime.datetime.strptime(g_time, '%Y-%m-%dT%H:%M:%S')

    @staticmethod
    def gmail_to_datetime(g_time):
        try:
            g_time = g_time[g_time.index(", ")+2:g_time.rindex(" +")]
        except:
            return datetime.datetime.now()
        return datetime.datetime.strptime(g_time, '%d %b %Y %H:%M:%S')


    @staticmethod
    def datetime_to_unix(dt = None):
        if dt is None:
            dt = datetime.datetime.now()
        
        return int(time.mktime(dt.timetuple()))

    @staticmethod
    def sort_index_from_date(parent_id, dt = None):
        if dt is None:
            dt = datetime.datetime.now()
        
        return SortIndex.get_for_date(parent_id, dt).get_value()
    
    @staticmethod
    def get_absolute_month_from_unix(ts_seconds = None):
        dt = DateUtils.unix_to_datetime(ts_seconds)
        
        return 12 * dt.year + dt.month
    
    @staticmethod
    def get_start_ts_of_month(absolute_month = None):
        if not absolute_month:
            absolute_month = DateUtils.get_absolute_month_from_unix()
        
        month_int = absolute_month%12
        year_int = int(absolute_month/12)
        
        #get the first of the month
        dt = datetime.datetime(year=year_int, month=month_int, day=1)
            
        return DateUtils.datetime_to_unix(dt)


from framework.models.domain.sort_index import SortIndex