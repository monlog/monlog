#REST API

from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource, ALL
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication
from log.models import LogMessage

class LogResource(ModelResource):
    class Meta:
        allowed_methods = ['post']
        queryset = LogMessage.objects.all()
        resource_name = "log"
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()

    def hydrate(self, bundle):
        bundle.obj.user = bundle.request.user
        return bundle

