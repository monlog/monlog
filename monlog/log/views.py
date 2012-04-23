# coding=utf8

from django.http import HttpResponse, HttpResponseBadRequest, QueryDict, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from models import LogMessage, Label, Expectation, SEVERITY_CHOICES
from django.contrib.auth.models import User
from monlog.log.forms import LogQueryForm, LabelForm, ExpectationForm
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

@login_required
def expectation(request, exp_name=None):
    """
    A view for editing expectations.
    """
    exp = None
    try:
        exp = Expectation.objects.get(expectation_name=exp_name, user=request.user)
    except Expectation.DoesNotExist:
        pass

    context = RequestContext(request)
    context['eqf'] = ExpectationForm(instance=exp)
    context['labels'] = Label.objects.filter(user=request.user)
    context['exp'] = exp

    context['active_expectation'] = exp_name
    context['expectations'] = Expectation.objects.filter(user=request.user)

    return render_to_response('expectation.html', context)

@login_required
def save_expectation(request):
    """
    Recieves a expectation form and creates an expectation from it. Redirects 
    to the expectation view afterwards.
    """

    form_data = request.POST.get('form_data')
    dict = {}
    for fd in form_data:
        dict[fd['name']] = fd['value']

    query_string = request.POST.get('query_string')

    id                      = dict['id']
    name                    = dict['expectation_name']
    _deadline               = dict['deadline']
    deadline = datetime[_deadline]

    tolerance_month         = dict['tolerance_0']
    tolerance_day           = dict['tolerance_1']
    tolerance_hour          = dict['tolerance_2']
    tolerance_minute        = dict['tolerance_3']
    tolerance_second        = dict['tolerance_4']

    repeat_month            = dict['repeat_0']
    repeat_day              = dict['repeat_1']
    repeat_hour             = dict['repeat_2']
    repeat_minute           = dict['repeat_3']
    repeat_second           = dict['repeat_4']

    tolerance = relativedelta(months  = tolerance_month,
                              days    = tolerance_day,
                              hours   = tolerance_hour,
                              minutes = tolerance_minute,
                              seconds = tolerance_seconds)
    repeat    = relativedelta(months  = repeat_month,
                              days    = repeat_day,
                              hours   = repeat_hour,
                              minutes = repeat_minute,
                              seconds = repeat_seconds)

    least_amount_of_results = dict['least_amount_of_results']

    try:
        expectation = Expectation.objects.get(id=id)
        expectation.expectation_name        = name
        expectation.original_deadline       = deadline
        expectation.deadline                = deadline
        expectation.tolerance               = tolerance
        expectation.repeat                  = repeat
        expectation.repeat_count            = 0
        expectation.least_amount_of_results = least_amount_of_results
    except Expectation.DoesNotExist:
        expectation = Expectation(
            user                    = request.user,
            expectation_name        = name,
            deadline                = deadline,
            original_deadline       = deadline,
            tolerance               = tolerance,
            repeat                  = repeat,
            repeat_count            = 0,
            least_amount_of_results = least_amount_of_results)

    expectation.save()
    return HttpResponse('/expectation/'+name)

def delete_expectation(request, exp_name):
    """
    Used when a user deletes an expectation
    """

    try:
        expectation = Expectation.objects.get(expectation_name=exp_name, user=request.user)
        expectation.delete()
    except Expectation.DoesNotExist:
        pass

    return HttpResponseRedirect('/')

@login_required
def list(request, label_name):
    """
    View for listing all log messages. Labels are used to filter which messages
    are displayed.
    """

    # Create a default LogQueryForm which is used if no label is specified.
    # Default is all severities checked, and order by datetime.
    qd = QueryDict('', mutable=True)
    qd.setlist('severity__in', [x[0] for x in SEVERITY_CHOICES])
    qd.setlist('order_by', ['-datetime'])
    lqf = LogQueryForm(qd)

    # Get label if user specified one.
    label_id = None
    if label_name:
        try:
            label = Label.objects.get(label_name=label_name, user=request.user)
            lqf = LogQueryForm(label.get_dict())
            label_id = label.id
        except Label.DoesNotExist:
            label_name = None

    # Set context variables
    context = RequestContext(request)
    context['lqf'] = lqf
    context['labels'] = Label.objects.filter(user=request.user)
    context['label_field'] = LabelForm(label_name)
    context['active_label'] = label_name
    context['label_id'] = label_id
    context['expectations'] = Expectation.objects.filter(user=request.user)
    return render_to_response('list.html', context)

@login_required
def save_label(request):
    """
    Used when a user saves a new label.
    """

    name = request.POST.get('name')
    query_string = request.POST.get('query_string')

    # Look for required fields
    if not name:
        logging.debug("Name not defined")
        return HttpResponseBadRequest("Required fields: name, query_string")
    if not query_string:
        logging.debug("Query_String not defined")
        return HttpResponseBadRequest("Required fields: name, query_string")

    # Look if label name already exists, overwrite it if it does.
    try:
        label = Label.objects.get(label_name=name, user=request.user)
        label.query_string=query_string
    except Label.DoesNotExist:
        label = Label(user=request.user,
                      label_name=name,
                      query_string=query_string)
    label.save()
    return HttpResponse('/label/'+name)

@login_required
def delete_label(request, label_id):
    """
    Used when a user deletes a label
    """

    try:
        label = Label.objects.get(pk=label_id, user=request.user)
        label.delete()
    except Label.DoesNotExist:
        pass

    return HttpResponseRedirect('/')
