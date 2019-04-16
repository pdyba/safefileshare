from django.contrib.auth.models import AnonymousUser


class UserAgentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if not isinstance(request.user, AnonymousUser):
            request.user.last_user_agent = request.META.get("HTTP_USER_AGENT")
            request.user.save()
        return self.get_response(request)
