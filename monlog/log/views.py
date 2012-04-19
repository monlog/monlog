# coding=utf8

from django.http import HttpResponse, HttpResponseBadRequest, QueryDict, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from models import LogMessage, Label, Expectation, SEVERITY_CHOICES
from django.contrib.auth.models import User
from monlog.log.forms import LogQueryForm, LabelForm, ExpectationForm
import logging

@login_required
def expectation(request, exp_name):
    """
    A view for editing expectations.
    """
    exp = None
    if exp_name:
        try:
            exp = Expectation.objects.get(expectation_name=exp_name, user=request.user)
            eqf = ExpectationForm(instance=exp)
        except Expectation.DoesNotExist:
            exp_name = None

    context = RequestContext(request)
    context['eqf'] = eqf
    context['labels'] = Label.objects.filter(user=request.user)
    context['exp'] = exp

    tolerance = u"± "
    # create ``tolerance`` string
    if exp.tolerance.months > 0:
        tolerance += "%s month(s)" % exp.tolerance.months
    if exp.tolerance.days > 0:
        tolerance += "%s day(s)" % exp.tolerance.days
    if exp.tolerance.hours > 0:
        tolerance += "%s hour(s)" % exp.tolerance.hours
    if exp.tolerance.minutes > 0:
        tolerance += "%s minute(s)" % exp.tolerance.minutes
    if exp.tolerance.seconds > 0:
        tolerance += "%s second(s)" % exp.tolerance.seconds
    context['exp_tolerance'] = tolerance

    # create ``repeat every``
    repeat = ""
    if exp.repeat.months > 0:
        repeat += "%s month(s)" % exp.repeat.months
    if exp.repeat.days > 0:
        repeat += "%s day(s)" % exp.repeat.days
    if exp.repeat.hours > 0:
        repeat += "%s hour(s)" % exp.repeat.hours
    if exp.repeat.minutes > 0:
        repeat += "%s minute(s)" % exp.repeat.minutes
    if exp.repeat.seconds > 0:
        repeat += "%s second(s)" % exp.repeat.seconds
    context['repeat'] = repeat

    context['active_expectation'] = exp_name
    context['expectations'] = Expectation.objects.filter(user=request.user)
    return render_to_response('expectation.html', context)

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
