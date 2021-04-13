from django.urls import path

from . import views
app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.content, name="page"),
    path("random/", views.random, name="random"),
    path("search/", views.search, name="search")
]
