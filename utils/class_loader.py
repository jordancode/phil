import importlib

from framework.config.config import Config


class ClassLoader:

    def __init__(self, config_name):
        
        #throws config exceptions
        self._config_name = config_name
        self._map = Config.get(config_name, "type_to_class")
        
    
    
    def get_class(self, type_id):
        if str(type_id) not in self._map :
            raise InvalidTypeError(type_id, self._config_name)
        
        dict = self._map[str(type_id)]
        
        module = importlib.import_module(dict["module"])
        
        class_ = getattr(module, dict["class"])
        
        return class_
    
    
    def get_type_id(self, class_):
        
        for type_id, dict in self._map.items():
            module = importlib.import_module(dict["module"])
            class_to_check = getattr(module, dict["class"])
            
            if class_to_check == class_ or issubclass(class_, class_to_check):    
                return int(type_id)
           
        raise InvalidTypeError(type_id, self._config_name)
    
    
    def get_type_id_from_name(self, name):
        for type_id, dict in self._map.items():
            if dict["name"] == name:
                return int(type_id)
        
        raise InvalidTypeError(type_id)
    
    def get_name_from_type_id(self, type_id):
        if str(type_id) not in self._map :
            raise InvalidTypeError(type_id, self._config_name)
        
        return self._map[str(type_id)]["name"]
        
        
                
class InvalidTypeError(Exception):
    _type_id = None
    _config_name = None
    
    def __init__(self,type_id = None, config_name = None):
        self._type_id = type_id
        self._config_name = config_name
    
    def __str__(self):
        if self._type_id is None:
            return "No type id found."
        elif self._config_name is None:
            return "None is not a valid config file name."
        
        return ("Invalid type provided: " + str(self._type_id) + "."
                " Type id and classes must be configured in " + str(self._config_name) + ".json")
        