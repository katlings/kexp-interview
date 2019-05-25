from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.now_playing, name='now_playing'),
    url(r'^last_commented$', views.last_commented, name='last_commented'),
]
