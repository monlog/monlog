from monlog.log.models import Expectation
from monlog.log.models import LogMessage
from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # check_expectation() list with errors
        # next_deadline() gets next deadline for current expectation.

        expectations = Expectation.objects.filter(deadline__lte=datetime.utcnow().isoformat())

        for expect in expectations:
            while expect.deadline < datetime.utcnow():
                errors, qs = expect.check_expectation()
                monlog_user = User.objects.get(username="monlog")
                message = LogMessage(server_ip='127.0.0.1', application=monlog_user, datetime=expect.deadline, long_desc="", short_desc="")

                message.long_desc += "Results: %s of %s" % (len(qs), expect.least_amount_of_results)

                # no errors found
                if len(errors) == 0:
                    # send info to db 1
                    message.severity = 1
                    message.short_desc = '%s reported OK' % expect.expectation_name

                else:
                    # errors found, send error to db 4
                    message.severity = 4
                    message.long_desc += "\n".join(errors[key] for key in errors.keys()) + "\n"
                    message.short_desc = '%s FAILED' % expect.expectation_name

                message.long_desc += "QuerySet: " % qs
                message.save()
                expect.deadline = expect.next_deadline()
                expect.save()
