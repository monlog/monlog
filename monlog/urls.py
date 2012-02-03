from django.conf.urls.defaults import patterns, include, url
from tastypie.api import Api
from log.api import LogResource

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(LogResource())

urlpatterns = patterns('',
    (r'^api/', include(v1_api.urls)),

    # Examples:
    # url(r'^$', 'monlog.views.home', name='home'),
    # url(r'^monlog/', include('monlog.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
