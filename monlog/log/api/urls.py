from django.conf.urls.defaults import patterns, include, url
from tastypie.api import Api
from monlog.log.api.api import LogResource
from monlog.log.api.api import LogCollectionResource

log_resource = LogResource()
log_collection = LogCollectionResource()

urlpatterns = patterns('',
    url(r'^', include(log_resource.urls)),   # API available with POST
    url(r'^', include(log_collection.urls)), # API available from GET
)
