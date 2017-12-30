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
    _host_type=None
    _template_dir=None
    
    _user = None
    
    
     
    def __init__(self, template_name=None, template_data=None, user=None, headers=None,host_type=None,template_dir=None):
        
        self.set_template(template_name)
        self._user = user
        self._host_type=host_type
        self._template_dir=template_dir
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
            host_type=self._host_type or "main"
            host_list=app_config['hosts']
            
            #populate alias keys
            for host_type, host_config in host_list.items():
                if 'host_alias' in host_config:
                    alias_config=host_list[host_config['host_alias']]
                    for k,v in alias_config.items():
                        if k not in alias_config:
                            alias_config[k]=v
            
            app_config["host_type"] = host_type
            app_config["www_url"] = AppUrl.get("web", host_type)
            app_config["api_url"] = AppUrl.get("api", host_type)
            app_config["assets_url"] = AppUrl.get("assets", host_type)
            app_config["admin_url"] = AppUrl.get("admin", host_type)
            
            ret['config_'] = {
                "app" : app_config,
                "www_url" : app_config["www_url"],
                "api_url" : app_config["api_url"],
                "assets_url" : app_config["assets_url"],
                "admin_url" : app_config["admin_url"],
                "app_json" : json.dumps(app_config)
             }
            
            if isinstance(self._user, Entity):
                ret["user_"] =self._user.to_dict(True,optional_keys=["email"])
                ret["user_json_"] =json.dumps(ret["user_"], default=self._json_helper)
        
        return ret
    
    def _render_template(self, template_name, template_data = None, partials = None):
        
        
            
        r = Renderer(search_dirs=[self._get_template_directory()],partials=partials)
        
        template_data = self._add_in_default_data(template_data)
        

        return r.render_name(template_name, template_data)

    def _fetch_template(self, template_name):
        loader = Loader(search_dirs=[self._get_template_directory()])
        
        return loader.load_name(template_name)
    
    def _get_template_directory(self):
        path=ROOT_PATH+"/static"
        if self._template_dir:
            path += "/"+self._template_dir
        path+="/template/"
        
        return path
    
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