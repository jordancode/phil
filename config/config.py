import copy
import json

from framework.config.environment import Environment
from app.utils.constants import ROOT_PATH


class Config:
    """
        Used for reading json config files
    """
    
    _config_cache = {}

    @classmethod
    def get(cls, file_name, key_path = None):
        config_dict = cls._get_dict_for_environment(file_name, Environment.get())
        
        return cls._get_config_by_key(config_dict,key_path,file_name)
    
    @classmethod
    def _get_dict_for_environment(cls, file_name, env_str):
        
        #populate cache
        if file_name in cls._config_cache:
            return cls._config_cache[file_name]
        
        envs_to_check = Environment.list()
        
        index = envs_to_check.index(env_str)
        envs_to_check = envs_to_check[index:]
        
        env_to_dir = {
                        Environment.PROD : "",
                        Environment.STAGE : "stage/",
                        Environment.DEV : "dev/"
                      }
        
        #check subdirectories for configs until correct one is found
        for env in envs_to_check:
            try:
                config_dict =  cls._get_dict_by_file_name(env_to_dir[env] + file_name)
                cls._config_cache[file_name] = config_dict
                return config_dict
            except ConfigFileNotFound:
                pass
            
        
        raise ConfigFileNotFound(file_name)
        
        
    @classmethod
    def _get_dict_by_file_name(cls, file_name):
        
        try:
            with open(ROOT_PATH+'/config/' + file_name + '.json') as data_file:
                config_dict = json.load(data_file)
        except IOError:
            raise ConfigFileNotFound(file_name)
        except ValueError:
            raise BadConfigFormatError(file_name)
        
        return config_dict
    
    @classmethod
    def _get_config_by_key(cls, config_dict, key, file_name):
        config_dict = copy.deepcopy(config_dict)
        """
            key is a string or array of strings for deeper access
        """
        
        if key is not None:
            
            if isinstance(key, str):
                key_arr = [key]
            else:
                key_arr = key

            for subkey in key_arr:
                if subkey in config_dict:
                    config_dict = config_dict[subkey]
                else:
                    raise ConfigKeyNotFoundError(key, file_name)
                
        return config_dict

        
class BadConfigFormatError(Exception):
    def __init__(self, config_name):
        self.config_name = config_name 
    def __str__(self):
        return self.config_name + ".json is not valid JSON format"     
        
class ConfigKeyNotFoundError(Exception):
    def __init__(self, key, config_name):
        self.key = key
        self.config_name = config_name 
    def __str__(self):
        return "key " + self.key + " not found in config " + self.config_name +".json"
    
class ConfigFileNotFound(Exception):
    def __init__(self, config_name):
        self.config_name = config_name 
    def __str__(self):
        return self.config_name + ".json file was not found"
    
    