from log.models import LogMessage
from django.db import models
from django import forms
from django.forms.widgets import CheckboxSelectMultiple,SelectMultiple, DateTimeInput
from log.models import SEVERITY_CHOICES
from django.contrib.auth.models import User
from django.http import QueryDict

class LogDateTime(DateTimeInput):
    input_type = 'datetime'

class LabelForm(forms.Form):
    label = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'placeholder':'Enter a label name...'}))

    def __init__(self, label_name, *args, **kwargs):
        super(LabelForm, self).__init__(*args, **kwargs)
        if label_name != None:
            self.fields['label'].widget.attrs['value'] = label_name

class LogQueryForm(forms.Form):
    search = forms.CharField(max_length=100,
                     widget=forms.TextInput(attrs={'class':'search-query', 'placeholder':'Search...'}))
    severity__in = forms.MultipleChoiceField(required=False, widget=CheckboxSelectMultiple(attrs={}), choices=SEVERITY_CHOICES)
    datetime__gte = forms.DateTimeField(required=False, widget=LogDateTime)
    datetime__lte = forms.DateTimeField(required=False, widget=LogDateTime)
    application__in = forms.MultipleChoiceField(required=False, widget=SelectMultiple, choices=())
    server_ip__in = forms.MultipleChoiceField(required=False, widget=SelectMultiple, choices=())

    def __init__(self, *args, **kwargs):
        super(LogQueryForm, self).__init__(*args, **kwargs)
        self.user_values = [(x['id'],x['username']) for x in User.objects.all().values()]
        self.servers = LogMessage.objects.all().order_by('server_ip').values('server_ip').distinct()
        self.server_values = [(x['server_ip'],x['server_ip']) for x in self.servers]

        data = []
        if isinstance(self.data, QueryDict):
            data = [int(x) for x in self.data.getlist('severity__in')] # get a list of all severity choices
        # Severity choices is a tuple of three elements where the third is whether the severity is checked or not. 
        # This is needed when displaying the buttons as active or not.
        self.severity_choices = [(choice[0], choice[1], choice[0] in data) for choice in SEVERITY_CHOICES]

        self.fields['application__in'] = forms.MultipleChoiceField(required=False, widget=SelectMultiple, choices=self.user_values)
        self.fields['server_ip__in'] = forms.MultipleChoiceField(required=False, widget=SelectMultiple, choices=self.server_values)

