from django.db import models
from django import forms
from django.forms.widgets import CheckboxSelectMultiple, SelectMultiple, DateTimeInput
from monlog.log.models import SEVERITY_CHOICES, LogMessage, Expectation, ExpectationMessage
from django.contrib.auth.models import User
from django.http import QueryDict
from dateutil.relativedelta import relativedelta
from datetime import datetime

class LabelForm(forms.Form):
    """
    Small form for saving label. The charfield is populated with 
    label name if it's available.
    """

    label = forms.CharField(
            label="",
            max_length=100,
            widget=forms.TextInput(attrs={
                'placeholder':'Enter a label name...'
            }))

    def __init__(self, label_name, *args, **kwargs):
        super(LabelForm, self).__init__(*args, **kwargs)
        if label_name is not None:
            self.fields['label'].widget.attrs['value'] = label_name

class LogQueryForm(forms.Form):
    """
    This is the form for the log message filter.
    """

    search = forms.CharField(
            max_length=100,
            widget=forms.TextInput(attrs={
                'class':'search-query',
                'placeholder':'Search...'
            }))
    severity__in = forms.MultipleChoiceField(
                        required=False,
                        widget=CheckboxSelectMultiple(attrs={}),
                        choices=SEVERITY_CHOICES)
    datetime__gte = forms.DateTimeField(
                        required=False,
                        widget=DateTimeInput)
    datetime__lte = forms.DateTimeField(
                        required=False,
                        widget=DateTimeInput)
    application__in = forms.MultipleChoiceField(
                        required=False,
                        widget=SelectMultiple,
                        choices=())
    server_ip__in = forms.MultipleChoiceField(
                        required=False,
                        widget=SelectMultiple,
                        choices=())

    def __init__(self, *args, **kwargs):
        super(LogQueryForm, self).__init__(*args, **kwargs)
        self.user_values = [(x['id'],x['username'])
                            for x
                            in User.objects.all().values()]
        self.servers = LogMessage.objects.all() \
                                         .order_by('server_ip') \
                                         .values('server_ip') \
                                         .distinct()
        self.server_values = [(x['server_ip'],x['server_ip'])
                              for x
                              in self.servers]

        data = []
        if isinstance(self.data, QueryDict):
            # get a list of all severity choices
            data = [int(x) for x in self.data.getlist('severity__in')]

        # Severity choices is a tuple of three elements where the third
        # is whether the severity is checked or not.
        # This is needed when displaying the buttons as active or not.
        self.severity_choices = [(choice[0], choice[1], choice[0] in data)
                                 for choice
                                 in SEVERITY_CHOICES]

        self.fields['application__in'] = forms.MultipleChoiceField(
                                            required=False,
                                            widget=SelectMultiple,
                                            choices=self.user_values)
        self.fields['server_ip__in'] = forms.MultipleChoiceField(
                                            required=False,
                                            widget=SelectMultiple,
                                            choices=self.server_values)

class RelativedeltaWidget(forms.MultiWidget):
    def __init__(self, widgets=None, *args, **kwargs):
        if widgets is None:
            widgets = [forms.TextInput(attrs={'style':'width:20px;'})
                       for x
                       in range(4)]
        super(RelativedeltaWidget, self).__init__(widgets, *args, **kwargs)

    def decompress(self, values):
        if values:
            return values
        return ""

    def _has_changed(self, initial, data):
        initial = (initial.months,
                   initial.days,
                   initial.hours,
                   initial.minutes)
        return initial == data

    def format_output(self, rendered_widgets):
        labels = [  "Mon",
                    "Day",
                    "Hou",
                    "Min",]
        output = []
        output.append("<table>")
        for widget in rendered_widgets:
            output.append("<td>")
            output.append("%s" %\
                                widget)
            output.append("</td>")
        output.append("</tr>")
        output.append("</table>")
        output.append("<span style='font-size:10px;'>")
        output.append("(Months / Days / Hours / Minutes)")
        output.append("</span>")
        return u'\n'.join(output)

class RelativedeltaField(forms.Field):
    """
    A field to provide ability to make relative deltas.

    FIXME
    This works, but is very inconvenient. The user must specify a correct
    relative delta as a string:
    "<months>_<days>_<hours>_<minutes>_<seconds>"

    example: 10 minutes would be "0_0_0_10_0"
    example: 2 months would be "2_0_0_0_0"
    """
    widget = RelativedeltaWidget

    def prepare_value(self, value):
        if value is not None:
            if not isinstance(value, relativedelta):
                value = self.clean(value)
            return (value.months + value.years*12,
                    value.days,
                    value.hours,
                    value.minutes)
        else:
            return None

    def clean(self, values):
        def to_int(v):
            try:
                return int(v)
            except:
                return 0
        (months, days, hours, minutes) = [to_int(v)
                                          for v
                                          in values]
        return relativedelta(months  = months,
                             days    = days,
                             hours   = hours,
                             minutes = minutes)

class ExpectationForm(forms.ModelForm):
    """
    This is the form for expectations
    """
    name = forms.CharField(
                     widget=forms.TextInput(attrs={
                'placeholder':'Enter an expectation name...'}))

    # timestamp for next deadline
    deadline = forms.DateTimeField(widget=DateTimeInput, initial=datetime.utcnow())

    # +- tolerance in relative delta
    # example: '+- 10 minute'
    tolerance = RelativedeltaField()

    # repeat every ``repeat`` relative delta
    # example: 'every 2 month'
    repeat = RelativedeltaField()

    least_amount_of_results = forms.IntegerField(initial=1)

    query_string = forms.CharField(widget=forms.HiddenInput)

    # Filter options
    search = forms.CharField(required=False, max_length=100,
                widget=forms.TextInput(attrs={'class':'search-query',
                                              'placeholder':'Search...'}))
    severity__in = forms.MultipleChoiceField(required=False,
                                             widget=SelectMultiple(attrs={
                                                 'size':'8',
                                                 }),
                                             choices=SEVERITY_CHOICES)
    application__in = forms.MultipleChoiceField(required=False,
                                              widget=SelectMultiple(attrs={
                                                 'size':'8',
                                                 }),
                                                choices=())
    server_ip__in = forms.MultipleChoiceField(required=False,
                                              widget=SelectMultiple(attrs={
                                                 'size':'8',
                                                 }),
                                              choices=())

    def __init__(self, data=None, *args, **kwargs):
        super(ExpectationForm, self).__init__(*args, **kwargs)
        self.user_values = [(x['id'],x['username']) 
                            for x in User.objects.all().values()]
        self.servers = LogMessage.objects.all() \
                                 .order_by('server_ip') \
                                 .values('server_ip') \
                                 .distinct()
        self.server_values = [(x['server_ip'],x['server_ip']) 
                              for x in self.servers]

        if data is None:
            data = QueryDict('')

        self.fields['severity__in'] = forms.MultipleChoiceField(
                            required=False,
                            widget=SelectMultiple(attrs={
                                 'size':'8',
                                 }),
                            choices=SEVERITY_CHOICES,
                            initial=data.getlist('severity__in'))
        self.fields['application__in'] = forms.MultipleChoiceField(
                            required=False,
                            widget=SelectMultiple(attrs={
                                 'size':'8',
                                 }),
                            choices=self.user_values,
                            initial=data.getlist('application__in'))
        self.fields['server_ip__in'] = forms.MultipleChoiceField(
                            required=False,
                            widget=SelectMultiple(attrs={
                                 'size':'8',
                                 }),
                            choices=self.server_values,
                            initial=data.getlist('server_ip__in'))

    def clean(self):
        """Creates the query_string from Filter parameters in the form"""
        cleaned_data = super(ExpectationForm, self).clean()
        qd = QueryDict(self.cleaned_data["query_string"], mutable=True)
        params = ["application__in",
                  "server_ip__in",
                  "severity__in",
                  "search"]
        for param in params:
            qd.setlist(param, cleaned_data[param])
        self.cleaned_data["query_string"] = qd.urlencode()
        return cleaned_data

    class Meta:
        model = Expectation
