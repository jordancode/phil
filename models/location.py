class Location:
    """
        represents a global location by lat and long
        can add methods to get interesting info from location
    """
    
    
    
    _lat = None
    _long = None
    
    
    def __init__(self, latitude, longitude):
        self._lat = latitude
        self._long = longitude
    
    @property 
    def lat(self):
        return self._lat
    
    @property
    def long(self):
        return self._long
    
    
    def to_tuple(self):
        return (self._lat, self._long)
    
    
    def _validate_latitude(self, lat):
        if lat < -90 or lat > 90:
            raise InvalidLatitudeError()
    
    def _validate_longitude(self, lat):
        if lat < -180 or lat > 180:
            raise InvalidLongitudeError()
        
    def to_dict(self, stringify_ids = False, optional_keys=None):
        return self._recursive_to_dict([], stringify_ids, optional_keys);
    
    def _recursive_to_dict(self, refs, stringify_ids = False, optional_keys=None):
        return {
                    "latitude" : self._lat,
                    "longitude" : self._long
                }
    

class InvalidCoordinateError(Exception):
    pass
      
class InvalidLatitudeError(InvalidCoordinateError):
    def __str__(self):
        return "Latitude must be in range [-90,90]"

class InvalidLongitudeError(InvalidCoordinateError):
    def __str__(self):
        return "Longitude must be in range [-180,180]"
    
    
     
            
    