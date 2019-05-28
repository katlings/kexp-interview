from django.conf.urls import url

from . import views

app_name = 'comment'
urlpatterns = [
    url(r'^$', views.now_playing, name='now_playing'),
#   url(r'^last_commented$', views.last_commented, name='last_commented'),
    url(r'^(?P<playid>[0-9]+)/add$', views.add_comment, name='add_comment'),
]
