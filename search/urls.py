from django.conf.urls import url
from django.views.generic import RedirectView
from .views import (search)
urlpatterns = [
    url(r'^search/$', search),
]
