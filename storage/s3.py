import tinys3

from framework.config.config import Config
from tinys3.request_factory import GetRequest
import pprint
import logging
import copy


class S3(tinys3.Connection):
    
    def __init__(self, temp_bucket=False):
        config = copy.deepcopy(Config.get("s3"))
        if temp_bucket:
            config["default_bucket"] = config["temp_bucket"]
        
        if "temp_bucket" in config:
            del config["temp_bucket"]
        
        super().__init__(**config)
        
        
    def get(self, key, bucket=None, headers=None):

        r = GetRequestWithHeaders(self, key, self.bucket(bucket), headers)

        return self.run(r)
    
class GetRequestWithHeaders(GetRequest):
    
    def __init__(self, conn, key, bucket, headers = None):
        self.headers = headers
        super().__init__(conn, key, bucket)
    
    def run(self):
        url = self.bucket_url(self.key, self.bucket)
        r = self.adapter().get(url, auth=self.auth, headers=self.headers)

        r.raise_for_status()

        return r
