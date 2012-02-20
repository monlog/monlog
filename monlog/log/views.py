from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from models import LogMessage, SEVERITY_CHOICES
from filters import LogMessageFilterSet
from django.contrib.auth.models import User

@login_required
def list(request):
    context = RequestContext(request)
    queryset = LogMessage.objects.all()
    context['severity_choices'] = SEVERITY_CHOICES
    context['application_choices'] = User.objects.all()
    context['server_choices'] = LogMessage.objects.all().order_by('server_ip').values('server_ip').distinct()
    context['filterset'] = LogMessageFilterSet(request.GET or None, queryset=queryset)
    return render_to_response('list.html', context)
