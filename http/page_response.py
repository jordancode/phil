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
        
    def _add_in_default_data(self, data):
        ret = super()._add_in_default_data(data)
        
        #add in the default file lists
        for file_type in ["css","js"]:
            l = Config.get(file_type,"urls")
            if file_type + "_" in ret:
                custom_list = ret[file_type + "_"]
                
                if type(custom_list) is str:
                    custom_list =  [ custom_list ]
                
                combined_list = l + custom_list
                new_list = []
                
                #dedupe and preserve order
                seen_urls = {}
                for url in combined_list:
                    if url not in seen_urls:
                        new_list.append(url)
                    seen_urls[url] = True
                    
                    
                ret[file_type + "_"] = new_list
            else:
                ret[file_type + "_"] = l
                
        #add in other things like title, meta
        if not "title_" in ret:
            ret['title_'] = Config.get("app","name")
        
        return ret
    
    def _get_partials(self):
        
        self_ = self
        
        class PartialFetcher:
            
            def get(self, partial_name):
                if partial_name == "content_" or partial_name == u"content_":
                    return self_._fetch_template(self_._template_name)
                else:
                    return self_._fetch_template(partial_name)
                    
                    
        return PartialFetcher()
        
        
    def _update_response(self):
        
        partials = self._get_partials()
        
        self.set_data(self._render_template(self.get_page_template(), self.get_template_data(),partials))
        
        
        
    