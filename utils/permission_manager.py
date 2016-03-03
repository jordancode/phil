from app.models.interactable import Interactable
from framework.models.data_access.data_access_object import RowDeletedException,\
    RowNotFoundException
from framework.models.domain.permissions import PermissionsMask,\
    PermissionsError


class PermissionManager:
    
    _logged_in_user = None
    
    def __init__(self, logged_in_user):
        self._logged_in_user = logged_in_user
    
    
    def verify_can_read(self, cls_, id_list):
        return self.verify_permissions(cls_, id_list, PermissionsMask(write=True))
    
    def verify_is_owner(self, cls_, id_list):
        return self.verify_permissions(cls_, id_list, PermissionsMask(owner=True))
    
    def verify_can_write(self, cls_, id_list):
        return self.verify_permissions(cls_, id_list, PermissionsMask(read=True))
    
    def verify_permissions(self, cls_, id_list, permissions_mask = PermissionsMask(read=True)):
        
        #make sure we have an iteractable type
        assert issubclass(cls_,Interactable)
        
        try:
            dao = cls_.getUserHasDAO()
            uhx_objs = dao.get_list(self._logged_in_user.id, id_list)
        except (RowDeletedException, RowNotFoundException):
            #verify ownership rows exist
            raise PermissionError()
        
        for uhx in uhx_objs:
            if not uhx.permission.has_mask(permissions_mask):
                #verify permissions
                raise PermissionsError()
        
        
        
        