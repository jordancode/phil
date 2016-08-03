from werkzeug.exceptions import HTTPException

from framework.http.json_response import JSONResponse
from framework.http.html_response import HTMLResponse


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
        
        resp = HTMLResponse(file_name, self.code)
        
        return resp