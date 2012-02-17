#REST API

from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource, ALL
from tastypie.authorization import DjangoAuthorization
from log.authentication import MonlogAuthentication
from log.authentication import CookieAuthentication
from log.models import LogMessage
from log.validation import LogValidation

class LogCollectionResource(ModelResource):
    """
    Allows a user to get log messages through GET requests. 

    User must be logged in and provide Djangos authentication cookie to be authenticated.
    """
    def build_filters(self, filters=None):
        """
        Currently, the purpose of this function is to enable use of multiple matches in a single field, i.e.
        /api/logmessages/?severity=0&severity=1
        """
        
        if filters is None:
            filters = {}

        orm_filters = super(LogCollectionResource, self).build_filters(filters)

        if "severity" in filters:
            del orm_filters["severity__exact"] #remove old filter
            orm_filters["severity__in"] = filters.getlist("severity")

        return orm_filters   


    class Meta:
        allowed_methods = ['get']
        queryset = LogMessage.objects.all()
        resource_name = "logmessages"
        authentication = CookieAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "severity" : ALL,
            "datetime" : ALL,
            "server_ip" : ALL,
            "application" : ALL,
        } 
        ordering = {
            "severity" : ALL,
            "datetime" : ALL,
            "server_ip" : ALL,
            "application" : ALL,
        }

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
    


