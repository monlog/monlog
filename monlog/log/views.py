from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from models import LogMessage, Label
from filters import LogMessageFilterSet

@login_required
def list(request):
    context = RequestContext(request)
    queryset = LogMessage.objects.all()
    context['filterset'] = LogMessageFilterSet(request.GET or None, queryset=queryset)
    return render_to_response('list.html', context)

@login_required
def save_label(request):
    """
    Used when a user saves a new label. 
    """
    context = RequestContext(request)
    context['name'] = request.POST.get('name')
    label = Label(label_name=request.POST.get('name'), query_string=request.POST.get('query_string') )
    label.save()
    return render_to_response('label_saved.html', context)
    
