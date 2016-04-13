from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Examples:
    # url(r'^$', 'luctor.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url('^', include('django.contrib.auth.urls')),
    url(r'^avatar/', include('avatar.urls')),
    url(r'^', include('recipes.urls', namespace='recipes')),
    url(r'^admin/', include(admin.site.urls)),
                           
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
