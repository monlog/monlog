#REST API

from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from log.authentication import MonlogAuthentication
from log.models import LogMessage
from log.validation import LogValidation
import re
from datetime import datetime


class LogResource(ModelResource):
    class Meta:
        allowed_methods = ['post']
        queryset = LogMessage.objects.all()
        resource_name = "log"
        authentication = MonlogAuthentication()
        authorization = DjangoAuthorization()
        validation = LogValidation()

    def hydrate(self, bundle):
        bundle.obj.application = bundle.request.user
        bundle.obj.server_ip = bundle.request.META['REMOTE_ADDR']
        return bundle
    


