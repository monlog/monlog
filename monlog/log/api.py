#REST API

from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource, ALL
from tastypie.authorization import DjangoAuthorization
from log.authentication import MonlogAuthentication
from log.authentication import CookieAuthentication
from log.models import LogMessage, SEVERITY_CHOICES
from log.validation import LogValidation


class ApplicationResource(ModelResource):
    """
    Used by LogCollectionResource to enable filtering on applications. 
    This resource is not available in the REST Api.
    """
    class Meta:
        allowed_methods=[]
        queryset = User.objects.all()
        fields= ['id','username']
        resource_name = "application"
        ordering = ['username']


class LogCollectionResource(ModelResource):
    """
    Allows a user to get log messages through GET requests. 

    User must be logged in and provide Djangos authentication cookie to be authenticated.
    """
    application = fields.ForeignKey(ApplicationResource, 'application', full=True)

    def dehydrate(self, bundle):
        if 'severity' in bundle.data:
            # translate numeric severity to text
            bundle.data['severity'] = SEVERITY_CHOICES[bundle.data['severity']][1]
        return bundle

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        else:
            filters = filters.copy()

        if 'datetime__gte' in filters:
            filters['datetime__gte'] = filters['datetime__gte'].replace("T", " ")
            filters['datetime__gte'] = filters['datetime__gte'].replace("Z", "")
        if 'datetime__lte' in filters:
            filters['datetime__lte'] = filters['datetime__lte'].replace("T", " ")
            filters['datetime__lte'] = filters['datetime__lte'].replace("Z", "")

        orm = super(LogCollectionResource, self).build_filters(filters)

        # if user doesn't specify severity level, no log messages will be returned.
        if "severity__in" not in filters:
            orm['severity__in'] = ""

        return orm

    class Meta:
        allowed_methods = ['get']
        queryset = LogMessage.objects.all()
        resource_name = "logmessages"
        authentication = CookieAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "severity" : ['in'],
            "datetime" : ['gte','lte'],
            "server_ip" : ['in'],
            "application" : ['in']
        }
        ordering = ["severity",
                    "datetime",
                    "server_ip",
                    "application"]

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
    


