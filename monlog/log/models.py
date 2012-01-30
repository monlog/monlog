from django.db import models

class LogMessage(models.Model):
    lid = models.IntegerField()
    date = models.DateTimeField()
    short_desc = models.CharField(max_length=100)
    long_desc = models.TextField()

    def __unicode__(self):
        return self.short_desc

    #def sanitize_timestamp(self):
        # Implement this.
