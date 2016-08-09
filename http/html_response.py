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
    
    
    
    def __init__(self, html_file=None, status = None, headers=None):
        
        if not status:
            status=200
        
        super().__init__(self._render_html(html_file), status=status, headers=headers, content_type="text/html")
    
    def _render_html(self, html_file):
        
        r = Renderer(search_dirs=[ROOT_PATH+"/static/html/"],file_extension="html")
        template_data =  r.render_name(html_file)
        
        return template_data