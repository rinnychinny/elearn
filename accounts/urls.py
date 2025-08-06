from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.student_register,
         name='student_register'),  # Registration
    # Post-login role selection
    path('dashboard/', views.role_landing, name='role_landing'),
]
