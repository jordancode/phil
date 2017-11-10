from framework.http.json_response import JSONResponse
from werkzeug.exceptions import HTTPException
from werkzeug.datastructures import Headers
import logging
import json

class BatchResponse(JSONResponse):
    
    """
        A response object that works with BatchRequest 
        It returns JSON with one key "batch" which contains a list of JSON response objects
    """
    
    _sub_responses = None
    
    def __init__(self, sub_responses):
        self._sub_responses = sub_responses
        
        headers = None
        
        for resp in sub_responses:
            try:
                if headers is None:
                    headers = resp.headers
                else:
                    headers = headers.extend(resp.headers)
                    
            except (AttributeError, TypeError):
                pass
        
        super().__init__(headers=headers, status=200)
        
        
    def _update_response(self):
        
        self._data_dict["batch"] = []
        
        for resp in self._sub_responses:
            
            # use the response version
            if isinstance(resp, HTTPException):
                resp = resp.get_response()
            
            
            if isinstance(resp, JSONResponse):
                self._data_dict["batch"].append(json.loads(resp._update_response()))
            else:
                self._data_dict["batch"].append(resp.get_data(True))
        
        return super()._update_response()
        
        
    
    
        
        