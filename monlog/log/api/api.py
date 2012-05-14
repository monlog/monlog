#REST API

from django.contrib.auth.models import User
from django.db.models import Q
from tastypie import fields
from tastypie.resources import ModelResource, ALL
from tastypie.authorization import DjangoAuthorization
from monlog.log.api.authentication import MonlogAuthentication
from monlog.log.api.authentication import CookieAuthentication
from monlog.log.models import LogMessage, ExpectationMessage, SEVERITY_CHOICES, Expectation
from monlog.log.api.validation import LogValidation
from datetime import datetime 
import logging

logger = logging.getLogger(__name__)

class ApplicationResource(ModelResource):
    """
    Used by LogCollectionResource to enable filtering on applications.
    This resource is not available in the REST Api.
    """
    class Meta:
        include_resource_uri = False
        allowed_methods=[]
        queryset = User.objects.all()
        fields= ['id','username']
        resource_name = "application"
        ordering = ['username']


class LogCollectionResource(ModelResource):
    """
    Allows a user to get log messages through GET requests.

    User must be logged in and provide Djangos authentication cookie
    to be authenticated.
    """
    application = fields.ForeignKey(ApplicationResource,
                                    'application',
                                    full=True)

    def dehydrate(self, bundle):
        if 'severity' in bundle.data:
            # translate numeric severity to text
            bundle.data['severity'] = SEVERITY_CHOICES[bundle.data['severity']][1]
        return bundle

    def build_filters(self, filters=None):
        if filters is None:
            filters = QueryDict('')
        filters._mutable = True

        # Create an OR'd filter for text searching in
        # long description and short description
        search_filter = {}
        if 'search' in filters:
            queryset = LogMessage.objects.filter(
                            Q(long_desc__icontains=filters['search']) |
                            Q(short_desc__icontains=filters['search']))
            search_filter = {'pk__in' : [i.pk for i in queryset]}
            del filters['search']

        orm = super(LogCollectionResource, self).build_filters(filters)
        orm.update(search_filter)
        return orm

    class Meta:
        include_resource_uri = False
        allowed_methods = ['get']
        queryset = LogMessage.objects.all()
        resource_name = "logmessages"
        authentication = CookieAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "severity" : ['in'],
            "datetime" : ['gte','lte'],
            "server_ip" : ['in'],
            "application" : ['in'],
            "add_datetime" : ['gte', 'lte'],
            "pk" : ['in']
        }
        ordering = ["severity",
                    "datetime",
                    "server_ip",
                    "application"]

class ExpectationResource(ModelResource):
    class Meta:
        include_resource_uri = False
        allowed_methods = []
        fields = ['id']
        queryset = Expectation.objects.all()
        resource_name = "expectation"

class ExpectationCollectionResource(LogCollectionResource):

    expectation = fields.ForeignKey(ExpectationResource,
                                    'expectation',
                                    full=True)

    class Meta(LogCollectionResource.Meta):
        include_resource_uri = False
        queryset = ExpectationMessage.objects.all()
        resource_name = "expectationmessages"
        filtering = {
                "expectation" : ALL
                }

class LogResource(ModelResource):
    """
    This is the API resource for inserting new log messages into the database.
    """
    class Meta:
        include_resource_uri = False
        allowed_methods = ['post']
        queryset = LogMessage.objects.all()
        resource_name = "log"
        authentication = MonlogAuthentication()
        authorization = DjangoAuthorization()
        validation = LogValidation()

    def hydrate(self, bundle):
        bundle.obj.application = bundle.request.user
        bundle.obj.server_ip = bundle.request.META['REMOTE_ADDR']
        timestamp = bundle.data["timestamp"]
        _datetime = datetime.utcfromtimestamp(float(timestamp))
        bundle.obj.datetime = _datetime
        # truncate short_desc if it's too long.
        if len(bundle.data["short_desc"]) > 100:
            logger.info("short_desc truncated. Full message: %s" %
                                bundle.data["short_desc"])
            bundle.data["short_desc"] = "%s%s" % (bundle.data["short_desc"][:86],
                                                  "...<truncated>")
        return bundle
