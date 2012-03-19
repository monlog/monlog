#!/usr/bin/env python

from monlog.log.models import Expectation as exp
from monlog.log.models import LogMessage as log
from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # check_expectation() list with errors
        # next_deadline() gets next deadline for current expectation.
        
        expectations = exp.objects.filter(deadline__lte=datetime.utcnow().isoformat())
        for expect in expectations:
            while expect.deadline < datetime.utcnow():
                errors, qs = expect.check_expectation()
                monlog_user = User.objects.get(username="monlog")
                message = log.LogMessage(server_ip='127.0.0.1', application=monlog_user, datetime=expect.deadline)
                
            # no errors found
                if len(errors) == 0:
                    # send info to db 1
                    message.severity = 1
                    message.long_desc = qs
                    message.short_desc = '%s reported OK' % expect.expectation_name
                    
                else:
                    # errors found, send error to db 4
                    message.severity = 4
                    message.long_desc = qs
                    message.short_desc = '%s FAILED' % expect.expectation_name
                    
                    message.save()
                    expect.deadline = next_deadline()
                    expect.save()
                    

        
    


if __name__ == '__main__':
    check_expectations()

    
                
        
