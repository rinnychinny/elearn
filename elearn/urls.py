"""
URL configuration for elearn project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),       # custom accounts urls
    # standard Django auth views
    path('accounts/', include('django.contrib.auth.urls')),
    path('courses/', include('courses.urls')),  # course urls
    path('chat/', include('chat.urls')),  # chat urls

    path('api/', include(('api.urls', 'api'), namespace='api')),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Schema & docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/',
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path('api/docs/redoc/',
         SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve local media files ONLY in local filesystem mode
if settings.DEBUG and getattr(settings, "MEDIA_URL", "")[:1] == "/":
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=getattr(settings, "MEDIA_ROOT", None),
    )
