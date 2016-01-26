from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, NotFound
from framework.http.cookie_session_store import CookieSessionStore
import string
import importlib
from framework.http.method_override_request import MethodOverrideRequest
from framework.http.json_response import JSONResponse
import logging
import pprint
from framework.config.environment import Environment

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
            
            self.pre_hook(request)
            
            response = self.call_controller(request, rule, args)
                          
        except HTTPException as e:
            response = e
            
        except Exception as e:
            logging.exception(e)
            response = JSONResponse(status=500)
            if Environment.get() != Environment.PROD:
                response.set_error(repr(e))
        
        return response
    
    def get_server_name(self):
        return "localhost"
    
    def pre_hook(self,request):
        pass
    
    def post_hook(self,request,response):
        pass
    
    def get_session_store(self,request):
        #override if want to store session id's another way on the client
        return CookieSessionStore()
    
    def call_controller(self, request, rule, args):
        session_store = self.get_session_store(request)
        controller_method = rule.update_rule_with_meta(request, session_store)
        
        response = controller_method(**args)
        
        return response

    def wsgi_app(self, environ, start_response):
        request = MethodOverrideRequest(environ)
        response = self.dispatch_request(request)
                    
        self.post_hook(request, response)
        
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


    

