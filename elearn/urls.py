"""
URL configuration for elearn project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),       # accounts app
    path('accounts/', include('django.contrib.auth.urls')),  # standard Django auth views
    path('courses/', include('courses.urls')), #course views
]
