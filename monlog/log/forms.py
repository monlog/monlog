from log.models import LogMessage
from django.db import models
from django import forms
from django.forms.widgets import CheckboxSelectMultiple,SelectMultiple
from log.models import SEVERITY_CHOICES
from django.contrib.auth.models import User

class LogQueryForm(forms.Form):
    user_values = [(x['id'],x['username']) for x in User.objects.all().values()] 
    servers = LogMessage.objects.all().order_by('server_ip').values('server_ip').distinct()
    server_values = [(x['server_ip'],x['server_ip']) for x in servers] 

    search = forms.CharField(max_length=100,
                     widget=forms.TextInput(attrs={'class':'search-query', 'placeholder':"Search..."}))
    severity__in = forms.MultipleChoiceField(required=False, widget=CheckboxSelectMultiple(attrs={'checked':'checked'}), choices=SEVERITY_CHOICES)
    application__in = forms.MultipleChoiceField(required=False, widget=SelectMultiple, choices=user_values)
    server_ip__in = forms.MultipleChoiceField(required=False, widget=SelectMultiple, choices=server_values)
