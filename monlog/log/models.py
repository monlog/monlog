from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key

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
    """ Model of a log message """
    severity = models.IntegerField(choices=SEVERITY_CHOICES)
    datetime = models.DateTimeField()
    server_ip = models.IPAddressField()
    application = models.ForeignKey(User)
    short_desc = models.CharField(max_length=100)
    long_desc = models.TextField()

    def __unicode__(self):
        return self.short_desc

    def pretty_severity(self):
        return SEVERITY_CHOICES[self.severity][1]

    def sanitize_timestamp(self):
        # Implement this.
        pass

    class Meta:
        ordering = ('-datetime',)

class Label(models.Model):
    """ Model of a search filter that may be saved """
    query_string = models.TextField()
    label_name = models.CharField(max_length=20,unique=True)
    def __unicode__(self):
        return self.label_name


