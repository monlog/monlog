from models import LogMessage
import django_filters

class LogMessageFilterSet(django_filters.FilterSet):
    class Meta:
        model = LogMessage
