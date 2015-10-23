import tinys3
from framework.config.config import Config

class S3(tinys3.Connection):
    
    def __init__(self):
        config = Config.get("s3")
        super().__init__(**config)
