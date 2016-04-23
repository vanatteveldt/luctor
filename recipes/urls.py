from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from recipes import views

urlpatterns = [
    url(r'^$', views.SearchView.as_view(), name='search'),
    url(r'^les/(?P<pk>[-\w]+)/$', views.LessonView.as_view(), name='lesson-detail'),
    url(r'^recept/(?P<pk>[-\w]+)/$', views.RecipeView.as_view(), name='recipe-detail'),
    url(r'^recept/(?P<pk>\d+)/add-picture$', views.AddPictureView.as_view(), name='picture-add'),
    url(r'^picture/(?P<pk>\d+)/delete$', views.DeletePictureView.as_view(), name='picture-delete'),
    url(r'^picture/(?P<pk>\d+)/like$', views.LikePictureView.as_view(), name='picture-like'),

    # admin views
    url(r'^upload$', staff_member_required(views.UploadView.as_view()), name='upload'),
    url(r'^check/(?P<pk>[-\w]+)/$', staff_member_required(views.CheckView.as_view()), name='check'),

]
