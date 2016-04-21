from framework.config.config import Config

"""
    Exports config variables for rq worker to read.
    
    Usage:
        cd /srv/www/photo_app 
        export ENV=<DEV|STAGE|PROD>
        rq worker -c framework.config.rq_worker_settings
"""

connection_config = Config.get("redis", "connection")
dbs_config = Config.get("redis", "dbs")

REDIS_HOST = connection_config.get("host")
REDIS_PORT = connection_config.get("port")

REDIS_DB = dbs_config.get("queue")

QUEUES = ['high','default','low']