#REST API

from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource, ALL
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication
from log.models import LogMessage

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'auth/user'
        filtering = { 'user' : ALL }
        fields = ['username']
#        excludes = ['email', 'password', 'is_superuser']

class LogResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')

    class Meta:
        allowed_methods = ['post']
        queryset = LogMessage.objects.all()
        resource_name = "log"
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()

