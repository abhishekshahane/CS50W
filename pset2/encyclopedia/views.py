from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from markdown2 import Markdown
from django import forms

from . import util
from random import choice

class CreateForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={'id': 'title'}))
    textarea = forms.CharField(widget=forms.Textarea(attrs={'cols': '10'}),  label='')
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
    if len(f)==1:
        result = "result"
    else:
        result="results"
    return render(request, "encyclopedia/search.html",{
        "f":f,
        "number": len(f),
        "result": result
    })
def create(request):
    if request.method=="POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["textarea"]
            if title not in util.list_entries():
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("encyclopedia:page", args=[title]))
            else:
                return render(request, "encyclopedia/create.html",{
                "form":form,
                "title_exists":True
            })
        else:
            return render(request, "encyclopedia/create.html",{
                "form":form
            })
    else:
        return render(request, "encyclopedia/create.html",{
            "form": CreateForm()
        })
def edit(request, title):
    if util.get_entry(title)==None:
        return render(request, "encyclopedia/404.html", {
            "name":title
        })
    else:
        return render(request, "encyclopedia/edit.html", {
            "form": CreateForm()
        })
    
    

        
