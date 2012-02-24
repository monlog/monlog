from log.models import LogMessage
from django.db import models
from django import forms
from django.forms.widgets import CheckboxSelectMultiple,SelectMultiple, DateTimeInput
from log.models import SEVERITY_CHOICES
from django.contrib.auth.models import User

class LogDateTime(DateTimeInput):
    input_type = 'datetime'
    

class LogQueryForm(forms.Form):
    search = forms.CharField(max_length=100,
                     widget=forms.TextInput(attrs={'class':'search-query', 'placeholder':'Search...'}))
    severity__in = forms.MultipleChoiceField(required=False, widget=CheckboxSelectMultiple(attrs={'checked':'checked'}), choices=SEVERITY_CHOICES)
    datetime__gte = forms.DateTimeField(required=False, widget=LogDateTime)
    datetime__lte = forms.DateTimeField(required=False, widget=LogDateTime)
    label = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder':'Enter a label name...'}))
    application__in = forms.MultipleChoiceField(required=False, widget=SelectMultiple, choices=())
    server_ip__in = forms.MultipleChoiceField(required=False, widget=SelectMultiple, choices=())
    
    def __init__(self):
        super(LogQueryForm, self).__init__()
        self.user_values = [(x['id'],x['username']) for x in User.objects.all().values()]
        self.servers = LogMessage.objects.all().order_by('server_ip').values('server_ip').distinct()
        self.server_values = [(x['server_ip'],x['server_ip']) for x in self.servers]
        self.fields['application__in'] = forms.MultipleChoiceField(required=False, widget=SelectMultiple, choices=self.user_values)
        self.fields['server_ip__in'] = forms.MultipleChoiceField(required=False, widget=SelectMultiple, choices=self.server_values)

