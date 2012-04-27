from django.conf.urls.defaults import patterns, include, url
from tastypie.api import Api
from monlog.log.api.api import LogResource
from monlog.log.api.api import LogCollectionResource
from monlog.log.api.api import ExpectationCollectionResource

log_resource = LogResource()
log_collection = LogCollectionResource()
expectation_collection = ExpectationCollectionResource()

urlpatterns = patterns('',
    url(r'^', include(log_resource.urls)),   # API available with POST
    url(r'^', include(log_collection.urls)), # API available from GET
    url(r'^', include(expectation_collection.urls)),
)
