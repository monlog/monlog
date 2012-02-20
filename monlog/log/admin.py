from django.contrib import admin
from tastypie.models import ApiKey
from log.models import LogMessage, Label

admin.site.register(ApiKey)
admin.site.register(LogMessage)
admin.site.register(Label)
