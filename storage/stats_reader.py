import requests
from framework.http.cookie_session_store import CookieSessionStore
from framework.config.config import Config
from framework.utils.date_utils import DateUtils
import pprint


FUNCTION_SUM="sum"
FUNCTION_AVG="avg"
FUNCTION_MIN="min"
FUNCTION_MAX="max"
FUNCTION_LAST="last"

VALID_FUNCS=[FUNCTION_SUM, FUNCTION_AVG, FUNCTION_MIN, FUNCTION_MAX, FUNCTION_LAST]

INTERVAL_1_MINUTE = 60
INTERVAL_1_HOUR = 3600
INTERVAL_1_DAY = 86400
INTERVAL_1_WEEK = 604800
INTERVAL_1_MONTH = 2592000



class StatsReader:
    
    def get_sum(self, stat_name, start_ts, end_ts=None):
        series = self.get_series(stat_name, start_ts, end_ts)
        
        return self._sum_series(series)
    
    """
        returns an array of arrays
        [
            [value0, unix_ts0],
            [value1, unix_ts1],
            ...
        ]
        
    """
    def get_series(self, stat_name, start_dt, end_dt=None, interval=INTERVAL_1_MINUTE, func=FUNCTION_SUM):
        url = self._get_renderer_url(stat_name, start_dt, end_dt, interval, func)
        response = self._make_request(url)
        if not len(response):
            return []
        
        return response[0]["datapoints"]
    
    
    def _get_graphite_endpoint(self):
        return Config.get("graphite","endpoint")
    
    def _get_graphite_session_id(self):
        return Config.get("graphite",["session","id"])
    
    def _get_graphite_session_token(self):
        return Config.get("graphite",["session","token"])
    
    
    def _sum_series(self, series):
        ret=0
        for [value, ts] in series:
            if value:
                ret+=value
        
        return ret
    
    
    def _get_renderer_url(self, stat_name, start_dt, end_dt=None, interval=INTERVAL_1_MINUTE, func=FUNCTION_SUM):
        url = self._get_graphite_endpoint()
        
        stat_name=stat_name+".count"
        url += "/render?"
        url += "target=summarize(" + stat_name + ',"' + str(interval) + 'second","' + func + '",true)'
        url += "&from=" + str(DateUtils.datetime_to_unix(start_dt))
        
        if end_dt:
            url += "&until=" + str(DateUtils.datetime_to_unix(end_dt))
        
        url += "&format=json"
        
        return url
    
    def _get_cookies(self):
        #bit of a hack here, but gets admin pages to work by 
        #passing a hard-coded session along with the request
        css=CookieSessionStore()
        cookies={
            css._get_cookie_name(): self._get_graphite_session_id(),
            css._get_token_cookie_name(): self._get_graphite_session_token()
        }
        return cookies
    
    def _make_request(self, url):
        response = requests.get(url,cookies=self._get_cookies())
        
        return response.json()
        
        
        
    
    
        
        