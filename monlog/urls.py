from django.conf.urls.defaults import patterns, include, url
from tastypie.api import Api
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'log.views.list'),
    url(r'^api/', include('log.api.urls')),
    url(r'^label/save', 'log.views.save_label'),
    url(r'^label/delete/(?P<label_id>\d+)', 'log.views.delete_label'),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', { 'template_name': 'login.html' }),

    url(r'^admin/jsi18n/', 'django.views.i18n.javascript_catalog'),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
