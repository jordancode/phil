from werkzeug.wrappers import (BaseResponse,ETagResponseMixin,
               CommonResponseDescriptorsMixin,
               WWWAuthenticateMixin)

class MediaResponse(BaseResponse,ETagResponseMixin,
               CommonResponseDescriptorsMixin,
               WWWAuthenticateMixin):
    
    """
        Generic response for non-text content
        
    """
    
    
    
    def __init__(self, asset_data, content_type, headers = None, status = 200):
        
        super().__init__(asset_data, status=status, headers=headers, content_type=content_type)
        
    
    
    @staticmethod
    def from_asset(asset):
        return MediaResponse(asset.data,asset.content_type)