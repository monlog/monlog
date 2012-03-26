from django.contrib.auth.models import User
from tastypie.models import ApiKey
from tastypie.http import HttpUnauthorized
from tastypie.authentication import Authentication

class CookieAuthentication(Authentication):
    """
    Handles auth from Session cookie provided by the user.
    """

    def _unauthorized(self):
        return HttpUnauthorized()

    def is_authenticated(self, request, **kwargs):
        """
        User is authenticated if the variable ``_auth_user_id`` is found in the session.
        """
        from django.contrib.sessions.models import Session
        if 'sessionid' in request.COOKIES:
            s = Session.objects.get(pk=request.COOKIES['sessionid'])
            if '_auth_user_id' in s.get_decoded():
                user = User.objects.get(id=s.get_decoded()['_auth_user_id'])
                request.user = user
                return True
        return self._unauthorized()


class MonlogAuthentication(Authentication):
    """
    Handles API key auth, in which a user provides an API key.

    Uses the ``ApiKey`` model that ships with tastypie. 
    """

    def _unauthorized(self):
        return HttpUnauthorized()

    def extract_apikey(self, request):
        """
        Extracts the API key from the request

        If both GET and POST dictionaries contains ``api_key``, POST will be used.
        """
        return request.GET.get('api_key') or request.POST.get('api_key')

    def get_username_from_api_key(self, api_key):
        """
        Gets the username connected to an API key.
        """
        try:
            key = ApiKey.objects.get(key=api_key)
            username = User.objects.get(username=key.user.username)
        except ApiKey.DoesNotExist, User.DoesNotExist:
            return self._unauthorized()

    def is_authenticated(self, request, **kwargs):
        """
        Finds the user associated with an API key.

        Returns either ``True`` if allowed, or ``HttpUnauthorized`` if not.
        """
        api_key = self.extract_apikey(request)

        if not api_key:
            return self._unauthorized()

        try:
            key = ApiKey.objects.get(key=api_key)
            user = User.objects.get(username=key.user.username)
        except ApiKey.DoesNotExist, User.DoesNotExist:
            return self._unauthorized()

        request.user = user
        return True

    def get_identifier(self, request):
        """
        Provides a unique string identifier for the requester.

        This implementation returns the username of the user or ``nouser`` if something went wrong.
        """
        api_key = self.extract_apikey(request)
        username = self.get_username_from_api_key(api_key)
        return username or 'nouser'

