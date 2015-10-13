from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, NotFound
from framework.http.cookie_session_store import CookieSessionStore
import string
import importlib
from framework.http.method_override_request import MethodOverrideRequest
from framework.http.json_response import JSONResponse

class BaseApplication():
    
    
    def __init__(self, routes):
        self._routes = routes
    
    def dispatch_request(self, request):
        adapter = self._routes.bind_to_environ(request.environ,server_name=self.get_server_name())
        try:
            rule, args = adapter.match(return_rule=True)  
            
            self.pre_hook(request)
            
            response = self.call_controller(request, rule, args)
            
            self.post_hook(request, response)
                          
        except HTTPException as e:
            return e
        
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
        endpoint = rule.endpoint
        module_name,method = endpoint.rsplit(".",1)
        class_name = string.capwords(module_name,"_").replace("_","")

        module = importlib.import_module("app.controllers." + module_name)
        
        class_ = getattr(module, class_name)
        
        session_store = self.get_session_store(request)
        response = getattr(class_(request,session_store),method)(**args)
        
        return response

    def wsgi_app(self, environ, start_response):
        request = MethodOverrideRequest(environ)
        response = self.dispatch_request(request)
        
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


    

