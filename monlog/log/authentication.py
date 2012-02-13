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
        api_key = request.GET.get('api_key') or request.POST.get('api_key')
        return api_key

    def extract_username(self, api_key):
        """
        Extracts the username from a string containing the API key.
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
        Provides a unique string identifier for the requestor.

        This implementation returns the user's username.
        """
        api_key = self.extract_apikey(request)
        username = self.extract_username(api_key)
        return username or 'nouser'

