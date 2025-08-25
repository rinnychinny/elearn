"""
URL configuration for elearn project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),       # custom accounts urls
    # standard Django auth views
    path('accounts/', include('django.contrib.auth.urls')),
    path('courses/', include('courses.urls')),  # course urls
    path('chat/', include('chat.urls')),  # chat urls
]

# for hosting files on the Django server in debug
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
