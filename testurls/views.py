from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext


def home_page(request, home_page_template):
    return render_to_response(home_page_template, locals(), context_instance=RequestContext(request))


def register_page(request, register_page_template):
    return render_to_response(register_page_template, locals(), context_instance=RequestContext(request))

