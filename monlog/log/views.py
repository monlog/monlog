from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from filters import LogMessageFilterSet

@login_required
def list(request):
    context = RequestContext(request)
    context['filterset'] = LogMessageFilterSet(request.GET or None)
    return render_to_response('list.html', context)
