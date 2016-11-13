import logging
import pprint
import sys
import traceback

from werkzeug.exceptions import HTTPException, NotFound

import framework.http.cookie_session_store
from framework.config.environment import Environment
from framework.http.json_response import JSONResponse
from framework.http.method_override_request import MethodOverrideRequest
from framework.http.batch_response import BatchResponse
from framework.http.batch_request import BatchRequest
from framework.config.routes import BATCH_REQUEST_KEY

class BaseApplication():
    ##
    
    _rule=None
    
    def __init__(self, routes):
        self._routes = routes
         
    
    def dispatch_request(self, request, adapter):
        try:
            rule, args = adapter.match(return_rule=True)
            if rule is None:
                print("---------- RAISE NOT FOUND")
                raise NotFound()
            
            self._rule = rule
            
            request.rule = rule
            response = self.call_controller(request, rule, args)

        except Exception as e:
            return self.get_response_from_error(e,request,adapter)
            
        return response
    
    def get_routes_adapter(self, environ):
        
        http_host=self.get_http_host_for_routing(environ)
        
        return self._routes.bind_to_environ(
                environ,
                server_name=http_host
            )
    
    def get_http_host_for_routing(self,environ=None):
        return None
    
    def pre_hook(self,request):
        pass
    
    def post_hook(self,request,response):
        pass
    
    def clean_up(self):
        pass
    
    def get_session_store(self,request):
        #override if want to store session id's another way on the client
        return framework.http.cookie_session_store.CookieSessionStore()
    
    
    def call_controller(self, request, rule, args):
        session_store = self.get_session_store(request)
        controller_method = rule.update_rule_with_meta(request, session_store)
        
        response = controller_method(**args)
        
        return response

    def wsgi_app(self, environ, start_response):
        
        adapter = self.get_routes_adapter(environ)
        
        if self._is_batch_request(adapter):
            
            #batch requests are handled differently
            request = BatchRequest(environ, self._routes)
            self.pre_hook(request)
            
            try:    
                sub_responses = []
                for sub_req, adptr in request.get_sub_requests():
                    sub_responses.append(self.dispatch_request(sub_req, adptr)) 
                
                response = BatchResponse(sub_responses)
                
            except Exception as e:
                response = self.get_response_from_error(e, request, adapter)
            
        else:
            request = MethodOverrideRequest(environ)
            request.override_method()
            
            self.pre_hook(request)
            
            adapter = self.get_routes_adapter(environ) #re-fetch adapter because method is overridden
            response = self.dispatch_request(request, adapter)
        
        self.post_hook(request, response)

        ret = response(environ, start_response)
        self.clean_up()
        
        return ret
    
    
    def get_response_from_error(self, e, request, adapter):
        self.log_error(request,e)
        
        response = JSONResponse(status=500)
        if Environment.get() != Environment.PROD:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            response.set_error(repr(e))
            response.set_key("traceback", traceback.format_exception(
                    exc_type, exc_value, exc_traceback
                ))
        else:
            response.set_error("An error occurred")
                
        return response
    
    def log_error(self, request, e):
        logging.getLogger().error("============ INTERNAL SERVER ERROR ============")
        logging.exception(e)
        logging.getLogger().error("============ INPUT ============")
        logging.getLogger().debug(request.method + " " + request.url)
        logging.getLogger().error("args: " + pprint.pformat(dict(request.args.items())))
        logging.getLogger().error("form: " +pprint.pformat(dict(request.form.items())))
        logging.getLogger().error("json: " +pprint.pformat(dict(request.json.items())))
        logging.getLogger().error("values: " +pprint.pformat(dict(request.values.items())))
    
    
    
    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)



    def _is_batch_request(self, adapter):
        try:
            m,args = adapter.match()
            return m == BATCH_REQUEST_KEY
        except Exception:
            return False
            
    

