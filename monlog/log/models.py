from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key
from django.http import QueryDict

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

