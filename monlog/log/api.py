#REST API

from tastypie.resources import ModelResource
from log.models import LogMessage

class LogResource(ModelResource):
    class Meta:
        queryset = LogMessage.objects.all()
        resource_name = "Log"
