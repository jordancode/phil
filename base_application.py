import logging
import pprint
import sys
import traceback

from werkzeug.exceptions import HTTPException, NotFound

import framework.http.cookie_session_store
from framework.config.environment import Environment
from framework.http.json_response import JSONResponse
from framework.http.method_override_request import MethodOverrideRequest


class BaseApplication():
    
    
    def __init__(self, routes):
        self._routes = routes
    
    def dispatch_request(self, request):
        adapter = self._routes.bind_to_environ(request.environ,server_name=self.get_server_name())
        try:
            rule, args = adapter.match(return_rule=True)
            if rule is None:
                raise NotFound()
            
            request.rule = rule
            
            response = self.call_controller(request, rule, args)
                          
        except HTTPException as e:
            response = e
            self.log_error(request, e)
            
        except Exception as e:
            #-- uncaught exception
            #-- print to screen and log
            self.log_error(request,e)
            response = JSONResponse(status=500)
            if Environment.get() != Environment.PROD:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                response.set_error(repr(e))
                response.set_key("traceback", traceback.format_exception(
                        exc_type, exc_value, exc_traceback
                    ))
        
        return response
    
    def get_server_name(self):
        return "localhost"
    
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
        request = MethodOverrideRequest(environ)
        
        self.pre_hook(request)
        
        response = self.dispatch_request(request)
                    
        self.post_hook(request, response)
        
        ret = response(environ, start_response)
        
        self.clean_up()
        
        return ret
    
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


    

