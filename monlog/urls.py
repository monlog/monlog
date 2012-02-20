from django.conf.urls.defaults import patterns, include, url
from tastypie.api import Api
from log.api import LogResource
from log.api import LogCollectionResource
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

log_resource = LogResource()
log_collection = LogCollectionResource()

urlpatterns = patterns('',
    url(r'^$', 'log.views.list'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', { 'template_name': 'login.html' }),
    url(r'^api/', include(log_resource.urls)),   # API available with POST
    url(r'^api/', include(log_collection.urls)), # API available from GET
    url(r'^label/', 'log.views.save_label'),
    # Examples:
    # url(r'^$', 'monlog.views.home', name='home'),
    # url(r'^monlog/', include('monlog.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
