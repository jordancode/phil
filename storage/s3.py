import tinys3

from framework.config.config import Config
from tinys3.request_factory import GetRequest
import pprint
import logging
import copy


class S3(tinys3.Connection):
    
    def __init__(self, temp_bucket=False, zip_bucket=False):
        key_whitelist=["access_key", "secret_key", "default_bucket", "tls", "endpoint"]
        
        config = Config.get("s3")
        temp_config={}

        
        if temp_bucket:
            temp_config["default_bucket"] = config["temp_bucket"]
        elif zip_bucket:
            temp_config["default_bucket"] = config["zip_bucket"]
        else:
            temp_config["default_bucket"] = config["default_bucket"]
        
        #copy over remaining keys
        for key in key_whitelist:
            if key in config and key not in temp_config:
                temp_config[key] = config[key]
        
        super().__init__(**temp_config)
        
        
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
