from log.models import LogMessage
from django.db import models
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from log.models import SEVERITY_CHOICES

class LogQueryForm(forms.Form):
    search = forms.CharField(max_length=100,
                     widget=forms.TextInput(attrs={'class':'search-query', 'placeholder':"Search..."}))
    severity__in = forms.MultipleChoiceField(required=False, widget=CheckboxSelectMultiple(attrs={'checked':'checked'}), choices=SEVERITY_CHOICES)
