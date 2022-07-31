from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

import recipes.urls
from recipes.views import RecipeSearchView
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView


urlpatterns = [
    # Examples:
    # url(r'^$', 'luctor.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #url('^', include('django.contrib.auth.urls')),

    url('^', include('django.contrib.auth.urls')),
    
    #url('^login/$', auth_views.login, name="login"),
    #url('^logout/$', auth_views.logout, name="logout"),
    #url('^password_reset/$', auth_views.password_reset, name="password_reset"),
    #url('^password_reset/done/$, [name='password_reset_done']
    #url('^password_change/$', auth_views.password_change, name="password_change"),
                       
    #url('^password_change/done/$', RedirectView.as_view(url='/'), name='password_change_done'),
    url(r'^', include(recipes.urls, namespace='recipes')),
    path(r'admin/', admin.site.urls),

]