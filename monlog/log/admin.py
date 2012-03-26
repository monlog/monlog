from django.contrib import admin
from tastypie.models import ApiKey
from log.models import LogMessage, Label, Filter, Expectation

# Register models which are accessible through django admin
admin.site.register(ApiKey)
admin.site.register(LogMessage)
admin.site.register(Label)
admin.site.register(Expectation)
