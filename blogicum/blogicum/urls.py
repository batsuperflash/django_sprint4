from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from blog import views as blog_views
from pages import views as pages_views


def force_500(request):
    return 1 / 0


handler403 = 'pages.views.permission_denied'
handler404 = 'pages.views.page_not_found_debug'
handler500 = 'pages.views.server_error'


urlpatterns = [
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', blog_views.registration, name='registration'),
    path('admin/', admin.site.urls),
    path('force-500/', force_500),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    urlpatterns += [
        path('<path:exception>', pages_views.page_not_found_debug),
    ]
