from monlog.log.models import Expectation, ExpectationMessage
from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        Script that retrieves all expectation that has a deadline earlier
        than 'now' and checks their status.
        The script logs the status of the expectations and sets new deadlines
        for them.
        """
        debug = 'debug' in args

        if debug: print "Retrieving expectations to check..."

        expectations = Expectation.objects \
                                  .filter(deadline__lte=datetime.utcnow().isoformat())
        if debug: print "Number of expectations found: %s " % len(expectations)

        for expect in expectations:
            while expect.deadline < datetime.utcnow():
                if debug:
                    print ("  Checking expectation \"%s\"" +
                           " with deadline \"%s\".") \
                            % (expect, expect.deadline.isoformat())

                errors, qs = expect.check_expectation()
                if debug:
                    print "    errors: \"%s\"" % errors
                    print "    queryset: %s" % qs

                try:
                    monlog_user = User.objects.get(username="monlog")
                except User.DoesNotExist:
                    # What to do?
                    if debug: print "User 'monlog' does not exist. Cannot log!"
                    return

                message = ExpectationMessage(server_ip='127.0.0.1',
                                             application=monlog_user,
                                             datetime=expect.deadline,
                                             long_desc="",
                                             short_desc="")

                message.long_desc += "Results: %s of %s" % \
                                        (len(qs),
                                         expect.least_amount_of_results)

                if len(errors) == 0:
                    # no errors found, log severity level ``info``
                    if debug: print "    Expectation OK!"
                    message.severity = 1
                    message.short_desc = '%s reported OK' % \
                                            expect.expectation_name

                else:
                    # errors found, log severity level ``error``
                    if debug:
                        print "    Expectation FAILED!"
                        print "\n".join(errors[key] for key 
                                                    in errors.keys()) + "\n"
                    message.severity = 4
                    message.long_desc += "\n".join(errors[key] for key
                                                                in errors.keys())
                    message.short_desc = '%s FAILED' % expect.expectation_name

                message.long_desc += "\nQuerySet: " % qs
                message.save()
                expect.repeat_count += 1
                expect.save()
