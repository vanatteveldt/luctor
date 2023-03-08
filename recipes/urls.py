from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from django.conf import settings
from django.conf.urls.static import static
from recipes import views
from recipes.menu import MenuAddView, MenuDetailView, MenuDeleteView, MenuAddRecipeView, MenuRecipeOrderView, \
    MenuRecipeRemoveView
app_name='recipes'
urlpatterns = [
    url(r'^$', views.RecipeSearchView.as_view(), name='search'),
    url(r'^les/(?P<pk>[-\w]+)/$', views.LessonView.as_view(), name='lesson-detail'),
    url(r'^recept/(?P<pk>[-\w]+)/$', views.RecipeView.as_view(), name='recipe-detail'),
    url(r'^recept/(?P<pk>\d+)/add-picture$', views.AddPictureView.as_view(), name='picture-add'),
    url(r'^picture/(?P<pk>\d+)/delete$', views.DeletePictureView.as_view(), name='picture-delete'),
    url(r'^picture/(?P<pk>\d+)/like$', views.LikePictureView.as_view(), name='picture-like'),
    url(r'^recepten/$', views.RecipesView.as_view(), name='recipe-list'),
    url(r'^recent/$', views.RecentRecipesView.as_view(), name='recent-recipe-list'),
    url(r'^favorites/$', views.FavRecipesView.as_view(), name='fav-recipe-list'),
    url(r'^les/$', views.LessonsView.as_view(), name='lesson-list'),
    url(r'^alle-lessen/$', views.AllLessonsView.as_view(), name='all-lesson-list'),
    url(r'^alle-recepten/$', views.AllRecipesView.as_view(), name='all-recipe-list'),
    url(r'^menus/$', views.MenusView.as_view(), name='menu-list'),

                  # admin views
    url(r'^upload$', staff_member_required(views.UploadView.as_view()), name='upload'),
    url(r'^check/(?P<pk>[-\w]+)/$', staff_member_required(views.CheckView.as_view()), name='check'),

    url(r'^user/(?P<pk>[-\w]+)/$', views.UserDetailView.as_view(), name='user-details'),
    url(r'^user/$', views.UserDetailView.as_view(), name='my-details'),
    url(r'^les/(?P<pk>[-\w]+)/aanwezig$', staff_member_required(views.ChangeAanwezigView.as_view()),
        name='lesson-aanwezig'),

    url(r'^menu/add/$', MenuAddView.as_view(), name='menu-add'),
    url(r'^menu/add-recipe/$', MenuAddRecipeView.as_view(), name='menu-add-recipe'),
    url(r'^menu/(?P<pk>\d+)/$', MenuDetailView.as_view(), name='menu-detail'),
    url(r'^menu/(?P<pk>\d+)/delete$', MenuDeleteView.as_view(), name='menu-delete'),
    url(r'^menu/(?P<menu>\d+)/(?P<recipe>\d+)/move/(?P<direction>up|down)$', MenuRecipeOrderView.as_view(),
        name='menu-recipe-move'),
    url(r'^menu/(?P<menu>\d+)/(?P<recipe>\d+)/remove/$', MenuRecipeRemoveView.as_view(), name='menu-recipe-remove'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
