from django.conf.urls import url

from recipes import views

urlpatterns = [
    url(r'^$', views.SearchView.as_view(), name='search'),
    url(r'^les/(?P<pk>[-\w]+)/$', views.LessonView.as_view(), name='lesson-detail'),
    url(r'^check$', views.CheckRedirectView.as_view(), name='check'),


]
