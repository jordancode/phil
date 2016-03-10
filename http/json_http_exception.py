from werkzeug.exceptions import HTTPException

from framework.http.json_response import JSONResponse


class JSONHTTPException(HTTPException):
    
    def __init__(self, exception_class):
        super().__init__()
        
        self.description = exception_class.description
        self.code = exception_class.code
        
        
    def get_response(self, environ=None):
        resp = JSONResponse()
        resp.set_error(self)
        
        return resp
        