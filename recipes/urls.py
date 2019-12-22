from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from recipes import views
from recipes.menu import MenuAddView, MenuDetailView, MenuDeleteView, MenuAddRecipeView, MenuRecipeOrderView, \
    MenuRecipeRemoveView

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

    url(r'^user/(?P<pk>[-\w]+)/$', views.UserDetailView.as_view(), name='user-details'),
    url(r'^user/$', views.UserDetailView.as_view(), name='my-details'),
    url(r'^les/(?P<pk>[-\w]+)/aanwezig$', staff_member_required(views.ChangeAanwezigView.as_view()), name='lesson-aanwezig'),

    url(r'^menu/add/$', MenuAddView.as_view(), name='menu-add'),
    url(r'^menu/add-recipe/$', MenuAddRecipeView.as_view(), name='menu-add-recipe'),
    url(r'^menu/(?P<pk>\d+)/$', MenuDetailView.as_view(), name='menu-detail'),
    url(r'^menu/(?P<pk>\d+)/delete$', MenuDeleteView.as_view(), name='menu-delete'),
    url(r'^menu/(?P<menu>\d+)/(?P<recipe>\d+)/move/(?P<direction>up|down)$', MenuRecipeOrderView.as_view(), name='menu-recipe-move'),
    url(r'^menu/(?P<menu>\d+)/(?P<recipe>\d+)/remove/$', MenuRecipeRemoveView.as_view(), name='menu-recipe-remove'),
]
