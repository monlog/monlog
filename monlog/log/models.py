from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key

models.signals.post_save.connect(create_api_key, sender=User)

SEVERITY_CHOICES = ( 
                    ('0', 'Debug'),
                    ('1', 'Info'),
                    ('2', 'Notify'),
                    ('3', 'Warning'),
                    ('4', 'Error'),
                    ('5', 'Critical'),
                    ('6', 'Alert'),
                    ('7', 'Emergency')
                   )

class LogMessage(models.Model):
    """ Model of a log message """
    severity = models.CharField(max_length=1, choices=SEVERITY_CHOICES)
    datetime = models.DateTimeField()
    server_ip = models.IPAddressField()
    application = models.ForeignKey(User)
    short_desc = models.CharField(max_length=100)
    long_desc = models.TextField()

    def __unicode__(self):
        return self.short_desc

    def sanitize_timestamp(self):
        # Implement this.
        pass
