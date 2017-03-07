from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', root_view),
    url(r'^logout/?$', logout_view),
    url(r'^([^/]+)\.([a-z]+)', download_view),
]
