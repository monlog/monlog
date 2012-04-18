from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key
from django.http import QueryDict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tastypie.utils import dict_strip_unicode_keys

models.signals.post_save.connect(create_api_key, sender=User)

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
    server_ip = models.GenericIPAddressField()
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

    def db_type(self, connection=None):
        """
        Current representation of RelativedeltaField in the database.
        """
        return 'char(30)'

    def to_python(self, value):
        """
        Creates a relativedelta object from what we get from the database.
        """
        if not value:
            return None
        if isinstance(value, (str, unicode)):
            #raises ValueError if split not possible.
            months, days, hours, minutes, seconds = [int(v) 
                                                    for v 
                                                    in value.split("_")]
            return relativedelta(months  = months,
                                 days    = days,
                                 hours   = hours,
                                 minutes = minutes,
                                 seconds = seconds)
        elif isinstance(value, relativedelta):
            return value
        else:
            return "wat"
            return None

    def get_db_prep_value(self, value, connection=None, prepared=False):
        """
        Concatenate unit and timedelta into a string.
        """
        return "%i_%i_%i_%i_%i" % (value.months,
                                   value.days,
                                   value.hours,
                                   value.minutes,
                                   value.seconds)

    def formfield(self, **kwargs):
        """
        Using a RelativedeltaField to represent this field in a form.
        """
        from monlog.log.forms import RelativedeltaField as RelativedeltaFormField
        defaults = { 'form_class' : RelativedeltaFormField }
        defaults.update(kwargs)
        return super(RelativedeltaField, self).formfield(**defaults)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

class Expectation(Filter):
    """
    Model for expectations.
    """

    expectation_name = models.CharField(max_length=20, unique=True)
    user             = models.ForeignKey(User)

    # timestamp for original deadline
    deadline          = models.DateTimeField()
    original_deadline = models.DateTimeField()


    # +- tolerance in relative delta
    # example: '+- 10 minute'
    tolerance = RelativedeltaField()

    # repeat every ``repeat`` relative delta
    # example: 'every 2 month'
    repeat       = RelativedeltaField()
    repeat_count = models.IntegerField()

    least_amount_of_results = models.IntegerField()

    def __unicode__(self):
        return self.expectation_name

    def apply_tolerance(self, querydict):
        """
        Applies startdate and enddate to a querydict.

        Startdate = Current Deadline - Tolerance
        Enddate   = Current Deadline + Tolerance
        """
        if self.deadline is None:
            print ("Error: Deadline must've been set before "
                   "applying tolerance to query string.")
            return querydict

        startdate = (self.deadline - self.tolerance)
        enddate   = (self.deadline + self.tolerance)

        querydict['datetime__gte'] = startdate.isoformat()
        querydict['datetime__lte'] = enddate.isoformat()
        return querydict

    def check_expectation(self):
        """
        Checks if X amount of log messages matches the filter.
        X is the least amount of log messages we need in order to accept
        the expectation.

        Returns a dict of errors and the queryset. If no errors was found
        an empty dict will be returned.
        """
        errors = {}
        qd = dict_strip_unicode_keys(QueryDict(self.query_string,mutable=True))
        qd = self.apply_tolerance(qd)
        qs = LogMessage.objects.filter(**qd)
        if len(qs) < self.least_amount_of_results:
            errors['not_enough_results'] = (
                "Not enough results found. Found:\"" +
                str(len(qs)) + "\" out of \"" +
                str(self.least_amount_of_results) + "\".")
        return (errors, qs)

    @property
    def next_deadline(self):
        """
        Returns next deadline as a datetime object.
        Does NOT change the deadline.
        """
        return self.original_deadline + \
               self.repeat * self.repeat_count

