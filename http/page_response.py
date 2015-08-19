from framework.http.template_response import TemplateResponse
from framework.config.config import Config
import copy

class PageResponse(TemplateResponse):

    DEFAULT_PAGE_TEMPLATE = "app"
    
    _page_template = None
    
    def __init__(self, template_name=None, template_data=None, headers=None, page_template_name=None):
        super().__init__(template_name,template_data,headers)
        
        self.set_page_template(page_template_name)
    
    
    def set_page_template(self,template_name):
        self._page_template = template_name
        
    def get_page_template(self):
        return self._page_template or self.DEFAULT_PAGE_TEMPLATE
    
    
    def get_template_data(self):
        #need to return clone so we don't append more than once
        ret = copy.copy(self._template_data)
        
        #add in the default file lists
        for file_type in ["css","js"]:
            list = Config.get(file_type,"urls")
            if hasattr(ret, file_type):
                ret[file_type].append(list)
                #convert to set (to eliminate dupes) then back to list
                ret[file_type] = list(set(ret[file_type]))
            else:
                ret[file_type] = list
        
        #add in other things like title, meta        
        
        return ret
        
        
    
    def _get_partials(self):
        
        self_ = self
        
        class PartialFetcher:
            
            def get(self, partial_name):
                if partial_name == "content" or partial_name == u"content":
                    return self_._fetch_template(self_._template_name)
                else:
                    return self_._fetch_template(partial_name)
                    
                    
        return PartialFetcher()
        
        
    def _update_response(self):
        
        partials = self._get_partials()
        
        self.set_data(self._render_template(self.get_page_template(), self.get_template_data(),partials))
        
        
        
    