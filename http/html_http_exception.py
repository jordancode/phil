from werkzeug.exceptions import HTTPException

from framework.http.json_response import JSONResponse
from framework.http.html_response import HTMLResponse
from app.utils.site_utils import SiteUtils


class HTMLHTTPException(HTTPException):
    
    def __init__(self, exception_class):
        super().__init__()
        
        if hasattr(exception_class, "description"):
            self.description = exception_class.description
        else:
            self.description = str(exception_class)
        
        if hasattr(exception_class, "code"):
            self.code = exception_class.code
        else:
            self.code = 500
        
        
    def get_response(self, environ=None):
        
        if self.code >= 500:
            file_name = "500"
        else:
            file_name = "400"
            
        host_key_match=None
        if environ:
            http_host = environ.get("HTTP_HOST")
            host_key_match,host_config_match=SiteUtils.get_host_config_match(http_host)
        
        resp = HTMLResponse(file_name, self.code, host_type=host_key_match)
        
        return resp