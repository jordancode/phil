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


class TemplateResponse(BaseResponse,ETagResponseMixin,
               CommonResponseDescriptorsMixin,
               WWWAuthenticateMixin):
    
    _template_name = None
    _template_data = None
    
    _user = None
    
    
    
    def __init__(self, template_name=None, template_data=None, user=None, headers=None):
        
        self.set_template(template_name)
        self._user = user
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
    
    def _add_in_default_data(self, data):
        #need to return clone so we don't append more than once
        if self._template_data is not None:
            ret = copy.copy(data)
        else:
            ret = {}
        
        if not "config_" in ret:
            app_config = Config.get("app")
            
            app_config["www_url"] = AppUrl.get("web")
            app_config["api_url"] = AppUrl.get("api")
            app_config["assets_url"] = AppUrl.get("assets")
            app_config["admin_url"] = AppUrl.get("admin")
            
            ret['config_'] = {
                "app" : app_config,
                "www_url" : app_config["www_url"],
                "api_url" : app_config["api_url"],
                "assets_url" : app_config["assets_url"],
                "admin_url" : app_config["admin_url"],
                "app_json" : json.dumps(app_config)
             }
            
            if isinstance(self._user, Entity):
                ret["user_"] =self._user.to_dict(True)
                ret["user_json_"] =json.dumps(ret["user_"], default=self._json_helper)
        
        return ret
    
    def _render_template(self, template_name, template_data = None, partials = None):
            
        r = Renderer(search_dirs=[ROOT_PATH+"/static/template/"],partials=partials)
        
        template_data = self._add_in_default_data(template_data)
        

        return r.render_name(template_name, template_data)

    def _fetch_template(self, template_name):
        loader = Loader(search_dirs=[ROOT_PATH+"/static/template/"])
        
        return loader.load_name(template_name)
    
    def _update_response(self):
        self.set_data(self._render_template(self._template_name, self._template_data))
    
        
    def _json_helper(self, value):
        
        #stringifies otherwise non-json nodes
        try:
            return value.to_dict(True, self._optional_keys)
        except AttributeError:
            pass
        
        try:
            return str(value)
        except AttributeError:
            pass
        
        raise TypeError()
      
        
        
    def get_wsgi_response(self, environ):
        self._update_response()
        
        return super().get_wsgi_response(environ)