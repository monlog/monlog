from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key
from django.http import QueryDict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tastypie.utils import dict_strip_unicode_keys
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

    def __init__(self, deadline=datetime.now(), tolerance_amount=10, tolerance_unit=4, repeat_delta=1, repeat_unit=0, least_amount_of_hits=1, label_name="Expectation", user=None):
        super(Expectation, self).__init__()
        self.deadline = datetime.now()
        self.tolerance_amount = tolerance_amount
        self.tolerance_unit = tolerance_unit
        self.repeat_delta = repeat_delta
        self.repeat_unit = repeat_unit
        self.least_amount_of_hits = least_amount_of_hits
        self.label_name = label_name
        self.apply_tolerance()

    def apply_tolerance(self):
        """
        Sets startdate and enddate for filter.

        Startdate = Deadline - Tolerance
        Enddate   = Deadline + Tolerance
        """
        if self.deadline is None:
            print "Error: Deadline must've been set before applying tolerance to query string."
            return

        td = Expectation.get_timedelta(self.tolerance_unit, self.tolerance_amount)
        if td is None:
            print "Error: Couldn't apply tolerance to Expectation"
            return

        startdate = (self.deadline - td)
        enddate   = (self.deadline + td)

        qs = QueryDict(self.query_string, mutable=True)
        qs['datetime__gte'] = startdate.isoformat().replace('T',' ')
        qs['datetime__lte'] = enddate.isoformat().replace('T',' ')
        self.query_string = qs.urlencode()

    def check_expectation(self):
        """
        Checks if X amount of log messages matches the filter.
        X is the least amount of log messages we need in order to accept the expectation.

        Returns a dict of errors. If no errors was found an empty dict will be returned.
        """
        errors = {}
        qd = dict_strip_unicode_keys(self.get_dict())
        qs = LogMessage.objects.filter(**qd)
        if len(qs) < self.least_amount_of_hits:
            errors['not_enough_results'] = "Not enough results found. Found: \"" + str(len(qs)) + "\" out of \"" + str(self.least_amount_of_hits) + "\"."
            #errors['queryset'] = qs    #we might want to return this

        return errors

    def next_deadline(self):
        """
        Returns next deadline as a datetime object. Does NOT change the deadline.
        """
        timedelta = Expectation.get_timedelta(self.repeat_unit, self.repeat_delta)
        if timedelta is not None:
            return self.deadline + timedelta
        else:
            print "Error: Couldn't get next deadline."
            return None

    @staticmethod
    def get_timedelta(unit, value):
        """
        Returns a timedelta object from specified unit and value. See ``EXPECTATION_UNITS`` for valid units.
        """
        if isinstance(unit, str): unit = get_expectation_unit_from_string(unit)
        if value is None:
            print "Error: Value error. ", value
            return None

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

    @staticmethod
    def get_expectation_unit_from_string(string):
        for x in EXPECTATION_UNITS:
            if x[1] == string.lower():
                return x[0]
        return -1

    @staticmethod
    def get_expectation_unit_from_int(i):
        for x in EXPECTATION_UNITS:
            if x[0] == i:
                return x[1]
        return ''
