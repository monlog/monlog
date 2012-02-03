from django.contrib import admin
from tastypie.models import ApiKey
from log.models import LogMessage

admin.site.register(ApiKey)
admin.site.register(LogMessage)
