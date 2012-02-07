#REST API

from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication
from tastypie.validation import Validation
from log.models import LogMessage
    

class LogResource(ModelResource):
    class Meta:
        allowed_methods = ['post']
        queryset = LogMessage.objects.all()
        resource_name = "log"
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
#        validation = FormValidation()

    def hydrate(self, bundle):
        bundle.obj.application = bundle.request.user
        bundle.obj.server_ip = bundle.request.META['REMOTE_ADDR']
        return bundle
    


