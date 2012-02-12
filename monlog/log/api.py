#REST API

from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from log.authentication import MonlogAuthentication
from tastypie.validation import Validation
from log.models import LogMessage
import re
from datetime import datetime

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
        authentication = MonlogAuthentication()
        authorization = DjangoAuthorization()
        validation = LogValidation()

    def hydrate(self, bundle):
        bundle.obj.application = bundle.request.user
        bundle.obj.server_ip = bundle.request.META['REMOTE_ADDR']
        return bundle
    


