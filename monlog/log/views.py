from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from models import LogMessage, SEVERITY_CHOICES
from django.contrib.auth.models import User
from log.forms import LogQueryForm

@login_required
def list(request):
    context = RequestContext(request)
    queryset = LogMessage.objects.all()
    lqf = LogQueryForm()
    context['lqf'] = lqf
    return render_to_response('list.html', context)
