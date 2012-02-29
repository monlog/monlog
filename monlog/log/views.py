from django.http import HttpResponse, HttpResponseBadRequest
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from models import LogMessage, Label, SEVERITY_CHOICES
from django.contrib.auth.models import User
from log.forms import LogQueryForm, LabelForm
import logging

@login_required
def list(request):
    context = RequestContext(request)
    queryset = LogMessage.objects.all()
    lqf = LogQueryForm()
    label_name = request.GET.get('label')
    
    if label_name:
        label = Label.objects.get(label_name=label_name)
        if label:
            lqf = LogQueryForm(label.get_dict())
    context['lqf'] = lqf
    context['labels'] = Label.objects.all()
    context['label_field'] = LabelForm()
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
        label = Label.objects.get(label_name=name)
        label.query_string=query_string
    except Label.DoesNotExist:
        label = Label(label_name=name, query_string=query_string)
    label.save()
    return HttpResponse('/?label='+name)


