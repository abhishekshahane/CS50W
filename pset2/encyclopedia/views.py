from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from . import util
from random import choice


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()

    })
def content(request, title):
    return render(request, "encyclopedia/page.html",{
        "title": title
    })
def random(request):
    li = util.list_entries()
    f = choice(li)
    print(f)
    return HttpResponseRedirect(f'/wiki/{f}')
    
