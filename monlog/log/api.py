#REST API

from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import Authentication
from tastypie.validation import Validation
from tastypie.http import HttpUnauthorized
from log.models import LogMessage
import re
from datetime import datetime

class LogAuthentication(Authentication):
    """
    Handles API key auth, in which a user provides an API key.

    Uses the ``ApiKey`` model that ships with tastypie. If you wish to use
    a different model, override the ``get_key`` method to perform the key check
    as suits your needs.
    """
    def _unauthorized(self):
        return HttpUnauthorized()

    def extract_apikey(self, request):
        api_key = request.GET.get('api_key') or request.POST.get('api_key')
        return api_key

    def extract_username(self, api_key):
        from django.contrib.auth.models import User
        try:
            username = User.objects.get(username=api_key.user.username)
        except User.DoesNotExist:
            return self._unauthorized()
    
    def is_authenticated(self, request, **kwargs):
        """
        Finds the user associated with an API key.

        Returns either ``True`` if allowed, or ``HttpUnauthorized`` if not.
        """

        from django.contrib.auth.models import User
        from tastypie.models import ApiKey

        api_key = self.extract_apikey(request)
        
        print "API-KEY: ", api_key
        if not api_key:
            return self._unauthorized()
        try:
            key = ApiKey.objects.get(key=api_key)
            user = User.objects.get(username=key.user.username)
            print "User: ", user.username
        except ApiKey.DoesNotExist:
            return self._unauthorized()
        except User.DoesNotExist:
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


class LogValidation(Validation):
    def is_valid(self, bundle, request=None):
        """
        Performs a check on ``bundle.data``to ensure it is valid.

        If the data is valid, an empty list (all valid) will be returned. If
        not, a list of errors will be returned.
        """

        data = bundle.data
        if data is None:
            data = {}

        
        errors = {}

        # Validate datetime
        if 'datetime' not in data:
            errors['datetime'] = 'Datetime not included in request.'
        else:
            DATETIME_REGEX = re.compile('^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})(T|\s+)(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2}).*?$')
            match = DATETIME_REGEX.search(data['datetime'])
            if match:
                dt_data = match.groupdict()
                try:
                    datetime_obj = datetime(int(dt_data['year']), int(dt_data['month']), int(dt_data['day']), 
                                        int(dt_data['hour']), int(dt_data['minute']), int(dt_data['second']))
                except ValueError:
                    errors['datetime'] = "ValueError: Datetime is wrong."
            else:
                errors['datetime'] = 'Datetime badly formatted'
        
        # Validate severity
        if 'severity' not in data:
            errors['severity'] = 'Severity level not inluded in request.'
        else:
            if data['severity'] < 0 or data['severity'] > 7:
                errors['severity'] = "Not supported severity level."
     
        return errors
    

class LogResource(ModelResource):
    class Meta:
        allowed_methods = ['post']
        queryset = LogMessage.objects.all()
        resource_name = "log"
        authentication = LogAuthentication()
        authorization = DjangoAuthorization()
        validation = LogValidation()

    def hydrate(self, bundle):
#        bundle.obj.application = bundle.request.user
#        bundle.obj.server_ip = bundle.request.META['REMOTE_ADDR']
        return bundle
    


