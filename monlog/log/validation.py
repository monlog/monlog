from tastypie.validation import Validation
from log.models import LogMessage
from django.contrib.auth.models import User
from datetime import datetime
import simplejson as json
import re

class LogValidation(Validation):
    def log_malformed_data(self, data, errors, bundle):
        """
        If data provided by client is corrupt or malformed, we handle it here
        by adding an extra log to the system by monlog, notifying the user about
        the problem.
        """
        client_ip = bundle.request.META["REMOTE_ADDR"]
        client_ip = {"client_ip" : client_ip}
        get_dict = bundle.request.GET
        desc = data        
        desc.update(client_ip)
        desc.update(get_dict)       
        desc = json.dumps(desc)
        current_date = datetime.datetime.now()
        monlog_user = User.objects.get(Username="monlog")
        severity = 4;
        current_date = datetime.now()
        desc = json.dumps(data)
        severity = 4
        server_ip = "127.0.0.1"

        short_desc = "Malformed data! %s" % ", ".join(errors.values())

        log = LogMessage(datetime=current_date,
                long_desc=desc,
                short_desc=short_desc,
                application=monlog_user,
                server_ip=server_ip,
                severity=severity)

        log.save()

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

        # this function posts as monlog on errors.
        if len(errors) > 0:
            self.log_malformed_data(data, errors, bundle)
        
        return errors
    

