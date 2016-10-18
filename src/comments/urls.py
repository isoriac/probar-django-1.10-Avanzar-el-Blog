from django.conf.urls import include, url

from .views import comment_hilo


urlpatterns = [
    url(r'^(?P<id>\d+)/$', comment_hilo, name='hilo'),
    # url(r'^(?P<slug>[\w-]+)/delete/$', views.post_delete),
]
