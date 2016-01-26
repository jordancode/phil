from framework.models.domain.entity import Entity

class EntityRelation(Entity):
    """
        represents a relationship between two entities
    """
    
    def __init__(self, id1, id2, id1_name, id2_name):
        super().__init__(str(id1) + "_" + str(id2))
        
        self._id1_name = id1_name
        self._id2_name = id2_name
        
        self._set_attr(id1_name,id1)
        self._set_attr(id2_name,id2)
        
    
    @property
    def id1(self):
        return self._get_attr(self._id1_name)
    
    @property
    def id2(self):
        return self._get_attr(self._id2_name)
    
    def to_dict(self, stringify_ids = False, optional_keys=None):
        d = super().to_dict(stringify_ids,optional_keys)
        del(d["id"])
        
        return d
    
    