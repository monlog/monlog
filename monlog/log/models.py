from django.contrib.auth.models import User
from django.db import models

class LogMessage(models.Model):
<<<<<<< HEAD
    user = models.ForeignKey(User)
=======
>>>>>>> 45807df395c011b138110dee8e594f10eb62b1a9
    date = models.DateTimeField()
    short_desc = models.CharField(max_length=100)
    long_desc = models.TextField()

    def __unicode__(self):
        return self.short_desc

    #def sanitize_timestamp(self):
        # Implement this.
