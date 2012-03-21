from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key
from django.http import QueryDict
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

models.signals.post_save.connect(create_api_key, sender=User)

EXPECTATION_UNITS = (
                    (0,'month'),
                    (1,'week'),
                    (2,'day'),
                    (3,'hour'),
                    (4,'minute'),
                    (5,'second')
                  )

SEVERITY_CHOICES = (
                    (0, 'debug'),
                    (1, 'info'),
                    (2, 'notify'),
                    (3, 'warning'),
                    (4, 'error'),
                    (5, 'critical'),
                    (6, 'alert'),
                    (7, 'emergency')
                   )

class LogMessage(models.Model):
    """
    Model of a log message
    """

    severity = models.IntegerField(choices=SEVERITY_CHOICES)
    datetime = models.DateTimeField()
    add_datetime = models.DateTimeField(auto_now_add=True)
    server_ip = models.IPAddressField()
    application = models.ForeignKey(User)
    short_desc = models.CharField(max_length=100)
    long_desc = models.TextField()

    def __unicode__(self):
        return self.short_desc

    def pretty_severity(self):
        """
        Return the string name of this log message severity.
        """
        return SEVERITY_CHOICES[self.severity][1]

    class Meta:
        ordering = ('-datetime',)


class Filter(models.Model):
    """
    Model of a search filter. This is used in expectations and labels.
    """

    class Meta:
        abstract = True

    query_string = models.TextField()

    def __unicode__(self):
        return self.query_string

    def get_dict(self):
        """
        Creates a ``QueryDict`` from the querystring of this label.
        """
        return QueryDict(self.query_string)

class Label(Filter):
    """
    Model for labels.
    """
    user = models.ForeignKey(User)
    label_name = models.CharField(max_length=20,unique=True)

    def __unicode__(self):
        return self.label_name


class Expectation(Label):
    """
    Model for expectations.
    """

    # timestamp for next deadline
    deadline = models.DateTimeField()

    # +- amount of unit
    # example: '+- 10 minute'
    tolerance_amount = models.IntegerField()
    tolerance_unit = models.IntegerField()

    # repeat every ``repeat_delta`` ``repeat_unit``
    # example: 'every 2 month'
    repeat_delta = models.IntegerField()
    repeat_unit = models.IntegerField()

    least_amount_of_hits = models.IntegerField()

    def apply_tolerance(self):
        """
        Sets startdate and enddate for filter.

        Startdate = Deadline - Tolerance
        Enddate   = Deadline + Tolerance
        """

        td = self.get_timedelta(self.tolerance_unit, self.tolerance_amount)
        if td is None:
            print "Couldn't apply tolerance to Expectation"
            return

        startdate = (self.deadline - td)
        enddate   = (self.deadline + td)

        qs = QueryDict(self.query_string, mutable=True)
        qs['datetime__gte'] = time.mktime(startdate.utctimetuple())
        qs['datetime__lte'] = time.mktime(enddate.utctimetuple())
        self.query_string = qs.urlencode()

    def check_expectation(self):
        """
        Checks if X amount of log messages matches the filter.
        X is the least amount of log messages we need in order to accept the expectation.
        """
        return LogMessage.objects.filter(self.get_dict()) >= self.least_amount_of_hits

    def next_deadline(self):
        """
        Returns next deadline as a datetime object. Does NOT change the deadline.
        """
        timedelta = self.get_timedelta(self.repeat_unit, self.repeat_delta)
        return self.deadline + timedelta

    def get_timedelta(self, unit, value):
        """
        Returns a timedelta object from specified unit and value. See ``EXPECTATION_UNITS`` for valid units.
        """
        if unit < 0 or unit >= len(EXPECTATION_UNITS):
            print "Error: Not valid time unit; ",  unit
            return None

        if unit == 0: # month
            return relativedelta(months=value)
        elif unit == 1: # week
            return relativedelta(weeks=value)
        elif unit == 2: # day
            return relativedelta(days=value)
        elif unit == 3: # hour
            return relativedelta(hours=value)
        elif unit == 4: # minute
            return relativedelta(minutes=value)
        elif unit == 5: # second
            return relativedelta(seconds=value)

