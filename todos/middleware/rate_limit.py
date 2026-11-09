import os
import time
from collections import defaultdict

from django.http import JsonResponse


class SimpleRateLimitMiddleware:
    WINDOW_SECONDS = 60
    MAX_REQUESTS = int(os.getenv('MAX_REQUESTS', '100'))
    _request_history = defaultdict(list)

    def __init__(self, get_response):
        self.get_response = get_response

    @classmethod
    def clear(cls):
        cls._request_history.clear()

    def __call__(self, request):
        if request.path.startswith('/api/'):
            now = time.time()
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            history = self._request_history[ip]
            history[:] = [timestamp for timestamp in history if now - timestamp < self.WINDOW_SECONDS]

            if len(history) >= self.MAX_REQUESTS:
                return JsonResponse(
                    {"error": "Too many requests.", "code": 429},
                    status=429,
                )

            history.append(now)
            self._request_history[ip] = history

        return self.get_response(request)
