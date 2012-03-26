#!/usr/bin/env python

from monlog.log.models import Expectation as exp
from monlog.log.models import LogMessage
from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        debug = True if 'debug' in args else False

        if debug: print "Retrieving expectations to check..."

        expectations = exp.objects.filter(deadline__lte=datetime.utcnow().isoformat())
        if debug: print "Number of expectations found: " + str(len(expectations))

        for expect in expectations:
            while expect.deadline < datetime.utcnow():
                if debug: print "  Checking expectation \"%s\" with deadline \"%s\". " % (str(expect), expect.deadline.isoformat())

                errors, qs = expect.check_expectation()
                if debug:
                    print "    errors: \"%s\"" % str(errors)
                    print "    queryset: %s" % str(qs)

                monlog_user = User.objects.get(username="monlog")
                message = LogMessage(server_ip='127.0.0.1', application=monlog_user, datetime=expect.deadline, long_desc="", short_desc="")

                message.long_desc += "Results: " + str(len(qs)) + " of " + str(expect.least_amount_of_results) + "\n"

                # no errors found
                if len(errors) == 0:
                    # send info to db 1
                    if debug: print "    Expectation OK!"
                    message.severity = 1
                    message.short_desc = '%s reported OK' % expect.expectation_name

                else:
                    # errors found, send error to db 4
                    if debug:
                        print "    Expectation FAILED!"
                        print "\n".join(errors[key] for key in errors.keys()) + "\n"
                    message.severity = 4
                    message.long_desc += "\n".join(errors[key] for key in errors.keys()) + "\n"
                    message.short_desc = '%s FAILED' % expect.expectation_name

                message.long_desc += "QuerySet: " + str(qs)
                message.save()
                expect.deadline = expect.next_deadline()
                expect.save()


if __name__ == '__main__':
    check_expectations()

