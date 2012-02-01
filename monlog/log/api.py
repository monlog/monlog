#REST API

from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from log.models import LogMessage

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'auth/user'
#        excludes = ['email', 'password', 'is_superuser']

class LogResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')

    class Meta:
        allowed_methods = ['get']
        queryset = LogMessage.objects.all()
        resource_name = "log"
        authorization = DjangoAuthorization()
