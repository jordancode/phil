from werkzeug.wrappers import (BaseResponse,ETagResponseMixin,
               CommonResponseDescriptorsMixin,
               WWWAuthenticateMixin)

from pystache import Renderer
from pystache.loader import Loader

class TemplateResponse(BaseResponse,ETagResponseMixin,
               CommonResponseDescriptorsMixin,
               WWWAuthenticateMixin):
    
    _template_name = None
    _template_data = None
    
    
    
    def __init__(self, template_name=None, template_data=None, headers=None):
        
        self.set_template(template_name)
        self.set_template_data(template_data)
        
        super().__init__(None, status=200, headers=headers, content_type="text/html")
        
    
    
    def set_template(self,template_name):
        self._template_name = template_name
    
    def get_template(self):
        return self._template_name
    
    def set_template_data(self,template_data):
        self._template_data = template_data
    
    def get_template_data(self):
        return self._template_data
    
    def _render_template(self, template_name, template_data = None, partials = None):
        r = Renderer(search_dirs=["../static/template/"],partials=partials)

        return r.render_name(template_name, template_data)

    def _fetch_template(self, template_name):
        loader = Loader(search_dirs=["../static/template/"])
        
        return loader.load_name(template_name)
    
    def _update_response(self):
        self.set_data(self._render_template(self._template_name, self._template_data))
        
        
        
    def get_wsgi_response(self, environ):
        self._update_response()
        
        return super().get_wsgi_response(environ)