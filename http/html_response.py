import copy
import json

from pystache import Renderer
from pystache.loader import Loader
from werkzeug.wrappers import (BaseResponse,ETagResponseMixin,
               CommonResponseDescriptorsMixin,
               WWWAuthenticateMixin)

from framework.config.config import Config
from framework.models.entity import Entity
from app.utils.constants import ROOT_PATH
from framework.config.app_url import AppUrl


class HTMLResponse(BaseResponse,ETagResponseMixin,
               CommonResponseDescriptorsMixin,
               WWWAuthenticateMixin):
    
    _template_name = None
    _template_data = None
    
    _user = None
    _host_type=None
    
    
    
    def __init__(self, html_file=None, status = None, headers=None, host_type=None):
        
        if not status:
            status=200
        
        self._host_type=host_type
        super().__init__(self._render_html(html_file), status=status, headers=headers, content_type="text/html")
        
    
    def _render_html(self, html_file):
        
        html_path=ROOT_PATH+"/static/"
        if self._host_type and self._host_type != "main":
            html_path+=self._host_type+"/html/"
        else:
            html_path+="html/"
        
        r = Renderer(search_dirs=[html_path],file_extension="html")
        template_data =  r.render_name(html_file)
        
        return template_data