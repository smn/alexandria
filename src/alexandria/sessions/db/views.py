from alexandria.sessions.db.models import *
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.http import HttpResponse

def _get_data():
    data = {}
    for item in Item.objects.filter(key__in=['name', 'phone', 'technology', 'useful']):
        question_container = data.setdefault(item.key, {})
        question_container.setdefault(item.value, 0)
        question_container[item.value] += 1
    return data

def home(request):
    json = simplejson.dumps(_get_data())
    return render_to_response("home.html", locals())

def json(request):
    json = simplejson.dumps(_get_data())
    return HttpResponse(json, content_type='application/javascript')