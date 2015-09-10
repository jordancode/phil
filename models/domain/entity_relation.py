from framework.models.domain.entity import Entity

class EntityRelation(Entity):
    """
        represents a relationship between two entities
    """
    
    
    def __init__(self, id1, id2):
        super().__init__(str(id1) + "_" + str(id2))
        
        self._set_attr("id1",id1)
        self._set_attr("id2",id1)
        
    
    @property
    def id1(self):
        return self._get
    
    @property
    def id2(self):
        return self._id2
    
    
    
    