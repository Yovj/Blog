from django.utils.deprecation import MiddlewareMixin
from django.utils.deprecation import MiddlewareMixin


class DisableCSRFCheck(MiddlewareMixin):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)

class MyTest(MiddlewareMixin):
    def process_response(self,request,response):
        response['Access-Control-Allow-Origin'] = '*'
        return response