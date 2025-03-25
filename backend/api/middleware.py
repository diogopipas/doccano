import os

from django.conf import settings
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
import logging

logger = logging.getLogger(__name__)


class RangesMiddleware(MiddlewareMixin):
    """Quick solution. See:
    https://stackoverflow.com/questions/14324250/byte-ranges-in-django/35928017#35928017
    """

    def process_response(self, request, response):
        if response.status_code != 200 or not hasattr(response, "file_to_stream"):
            return response
        http_range = request.META.get("HTTP_RANGE")
        if not (http_range and http_range.startswith("bytes=") and http_range.count("-") == 1):
            return response
        if_range = request.META.get("HTTP_IF_RANGE")
        if if_range and if_range != response.get("Last-Modified") and if_range != response.get("ETag"):
            return response
        f = response.file_to_stream
        statobj = os.fstat(f.fileno())
        start, end = http_range.split("=")[1].split("-")
        if not start:  # requesting the last N bytes
            start = max(0, statobj.st_size - int(end))
            end = ""
        start, end = int(start or 0), int(end or statobj.st_size - 1)
        assert 0 <= start < statobj.st_size, (start, statobj.st_size)
        end = min(end, statobj.st_size - 1)
        f.seek(start)
        old_read = f.read
        f.read = lambda n: old_read(min(n, end + 1 - f.tell()))
        response.status_code = 206
        response["Content-Length"] = end + 1 - start
        response["Content-Range"] = "bytes %d-%d/%d" % (start, end, statobj.st_size)
        return response


def to_django_header(header):
    return f"HTTP_{header.replace('-', '_').upper()}"


class HeaderAuthMiddleware(RemoteUserMiddleware):
    header = to_django_header(settings.HEADER_AUTH_USER_NAME)

    def process_request(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        # Log request context
        logger.info(f"[Auth Flow] Request method: {request.method}, Path: {request.path}")
        logger.info(f"[Auth Flow] CSRF Token: {request.META.get('CSRF_COOKIE')}, Session ID: {request.session.session_key}")
        
        # Log all authentication related headers
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        logger.info(f"[Auth Flow] Authorization header: {auth_header}")
        logger.info(f"[Auth Flow] Custom auth header ({self.header}): {request.META.get(self.header)}")
        
        # Log CSRF related information
        csrf_token = request.META.get('CSRF_COOKIE')
        csrf_header = request.META.get('HTTP_X_CSRFTOKEN')
        csrf_middleware_token = request.META.get('CSRF_COOKIE_USED')
        logger.info(f"[Auth Flow] CSRF validation - Cookie Token: {csrf_token}, Header Token: {csrf_header}, Middleware Token: {csrf_middleware_token}")
        logger.info(f"[Auth Flow] Request Headers: {dict(request.headers)}")
        
        # Log current authentication state
        if request.user.is_authenticated:
            logger.info(f"[Auth Flow] User already authenticated as {request.user.username}")
            return

        username = request.META.get(self.header)
        if not username:
            logger.warning(f"No username found in header {self.header}")
            return

        super().process_request(request)
        self.process_user_groups(request.user, request.META)

    @classmethod
    def process_user_groups(cls, user, headers):
        if not user.is_authenticated:
            return

        groups = cls.parse_user_groups_from_header(headers)

        is_superuser = settings.HEADER_AUTH_ADMIN_GROUP_NAME in groups
        if user.is_superuser != is_superuser:
            user.is_superuser = is_superuser
            user.save()

    @classmethod
    def parse_user_groups_from_header(cls, headers):
        try:
            groups_header = headers[to_django_header(settings.HEADER_AUTH_USER_GROUPS)]
        except KeyError:
            return []
        else:
            return groups_header.split(settings.HEADER_AUTH_GROUPS_SEPERATOR)
