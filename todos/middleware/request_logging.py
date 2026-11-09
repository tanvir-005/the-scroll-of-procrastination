import logging
import time

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time
        user = getattr(request.user, 'username', 'anonymous')

        logger.info(
            "%s %s %s - %.3fs user=%s",
            request.method,
            request.path,
            response.status_code,
            duration,
            user
        )

        return response