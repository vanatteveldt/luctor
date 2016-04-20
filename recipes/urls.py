from django.conf.urls import url

from recipes import views

urlpatterns = [
    url(r'^$', views.SearchView.as_view(), name='search'),
    url(r'^les/(?P<pk>[-\w]+)/$', views.LessonView.as_view(), name='lesson-detail'),
    url(r'^recept/(?P<pk>[-\w]+)/$', views.RecipeView.as_view(), name='recipe-detail'),
    url(r'^check$', views.CheckRedirectView.as_view(), name='check'),
    url(r'^upload$', views.UploadView.as_view(), name='upload'),
    url(r'^check/(?P<pk>[-\w]+)/$', views.CheckView.as_view(), name='check'),
]
