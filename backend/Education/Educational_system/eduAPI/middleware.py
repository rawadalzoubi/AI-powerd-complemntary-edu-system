import re
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class DisableCSRFMiddleware(MiddlewareMixin):
    """
    Middleware to disable CSRF protection for API endpoints
    """
    def process_request(self, request):
        # Check if the request path matches any of the exempt URLs
        if hasattr(settings, 'CSRF_EXEMPT_URLS'):
            for pattern in settings.CSRF_EXEMPT_URLS:
                if re.match(pattern, request.path):
                    setattr(request, '_dont_enforce_csrf_checks', True)
                    break
        return None