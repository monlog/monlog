from django.contrib.auth.models import User
from django.db import models

class LogMessage(models.Model):
    user = models.ForeignKey(User)
    date = models.DateTimeField()
    short_desc = models.CharField(max_length=100)
    long_desc = models.TextField()

    def __unicode__(self):
        return self.short_desc

    #def sanitize_timestamp(self):
        # Implement this.
