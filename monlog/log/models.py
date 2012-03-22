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


class RelativedeltaField(models.Field):

    description = "A relative timedelta"

    __metaclass__ = models.SubfieldBase

    def __init__(self, unit, delta=0, *args, **kwargs):
        self.unit = unit
        self.delta = delta
        super(RelativedeltaField, self).__init__(*args, **kwargs)

    def db_type(self):
        """
        Representation in DB wouldn't need more than 3 letters for delta value, and 3 letters for unit value
        """
        return 'char(8)' # at most VVV_UUU    V=value, U=unit, _=delimiter

    def to_python(self, value):
        """
        Creates a relativedelta object from what we get from the database.
        """
        if not value:
            return None
        if isinstance(value, str):
            val, unit = value.split("_") #raises ValueError if split not possible.

            if unit == 'month':
                return relativedelta(months=int(val))
            elif unit == 'week':
                return relativedelta(weeks=int(val))
            elif unit == 'day':
                return relativedelta(days=int(val))
            elif unit == 'hour':
                return relativedelta(hours=int(val))
            elif unit == 'minute':
                return relativedelta(minutes=int(val))
            elif unit == 'second':
                return relativedelta(seconds=int(val))
            else:
                #invalid unit type
                raise TypeError('Invalid unit type: %s' % unit)
        elif isinstance(value, relativedelta):
            return value
        else:
            return None

    def get_db_prep_value(self, value):
        """
        Concatenate unit and timedelta into an at most 8-letter string.
        """
        return "%s_%s" % self.unit, self.delta

    def formfield(self, **kwargs):
            defaults = { 'form_class' : forms.CharField() }
            defaults.update(kwargs)
            return super(RelativedeltaField, self).formfield(**kwargs)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

class Expectation(Label):
    """
    Model for expectations.
    """

    # timestamp for next deadline
    deadline = models.DateTimeField()

    # +- amount of unit
    # example: '+- 10 minute'
    tolerance = RelativedeltaField()

    # repeat every ``repeat_delta`` ``repeat_unit``
    # example: 'every 2 month'
    repeat = RelativedeltaField()

    least_amount_of_hits = models.IntegerField()

    def __init__(self, deadline=datetime.now(), tolerance=relativedelta(minute=10), repeat=relativedelta(month=1), least_amount_of_hits=1, label_name="Expectation", user=None):
        super(Expectation, self).__init__()
        self.deadline = datetime.now()
        self.tolerance = tolerance
        self.repeat = repeat
        self.least_amount_of_hits = least_amount_of_hits
        self.label_name = label_name

    def apply_tolerance(self):
        """
        Sets startdate and enddate for filter.

        Startdate = Deadline - Tolerance
        Enddate   = Deadline + Tolerance
        """
        if self.deadline is None:
            print "Error: Deadline must've been set before applying tolerance to query string."
            return

        startdate = (self.deadline - self.tolerance)
        enddate   = (self.deadline + self.tolerance)

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
        return self.deadline + self.repeat

