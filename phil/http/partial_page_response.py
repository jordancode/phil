from werkzeug.wrappers import (BaseResponse,ETagResponseMixin,
               CommonResponseDescriptorsMixin,
               WWWAuthenticateMixin)

from framework.http.template_response import TemplateResponse

from pystache import Renderer
from pystache.loader import Loader

class PartialPageResponse(TemplateResponse):
    pass