from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from markdown2 import Markdown

from . import util
from random import choice


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()

    })
def content(request, title):
    if util.get_entry(title)==None:
        return render(request, "encyclopedia/404.html", {
            "name":title
        })
    a = util.get_entry(title)
    converter = Markdown()
    html = converter.convert(a)
    print(html)
    return render(request, "encyclopedia/page.html",{
        "title": title,
        "content": html
    })
def random(request):
    li = util.list_entries()
    f = choice(li)
    print(f)
    return HttpResponseRedirect(f'/wiki/{f}')
def search(request):
    q = request.GET.get('q')
    li = util.list_entries()
    f = []
    # We redirect user to the page immediately, if the entry matches a page 
    if q in li:
        return HttpResponseRedirect(reverse('encyclopedia:page', args=[q]))
    # It might be a substring - Even if it isn't, {% empty %} handles that
    for each in li:
        if q.lower() in each.lower():
            f+=[each]
    return render(request, "encyclopedia/search.html",{
        "f":f
    })
    
    

        
