from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static


from django.views.static import serve
from django.contrib.staticfiles.urls import staticfiles_urlpatterns 


urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),

    path('admin/', admin.site.urls),
    path('', include('chat.urls')),
    path('', include('user_account.urls'))
]
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
