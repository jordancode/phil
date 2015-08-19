import os

class Environment:
    
    DEV = "DEV"
    STAGE = "STAGE"
    PROD = "PROD"
    
    @staticmethod
    def get():
        current_env = os.environ.get("ENV", Environment.DEV)
       
        if current_env in Environment.list():
            return current_env
       
        return Environment.DEV
       
        
    @staticmethod
    def list():
        return [
                Environment.DEV,
                Environment.STAGE,
                Environment.PROD
                ]