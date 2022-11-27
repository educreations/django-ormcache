
from django.http.response import HttpResponse
from django.urls import path


def empty_view(request):
    return HttpResponse()


urlpatterns = [
    path("/", empty_view, name="home"),
]
