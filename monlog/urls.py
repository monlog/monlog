from django.conf.urls.defaults import patterns, include, url
from tastypie.api import Api
from log.api import LogResource
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

log_resource = LogResource()

urlpatterns = patterns('',
    url(r'^$', 'log.views.index'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', { 'template_name': 'login.html' }),
    (r'^api/', include(log_resource.urls)),
    # Examples:
    # url(r'^$', 'monlog.views.home', name='home'),
    # url(r'^monlog/', include('monlog.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
