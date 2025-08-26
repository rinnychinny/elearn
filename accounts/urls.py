from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = 'accounts'

urlpatterns = [
    path('register/', views.student_register,
         name='student_register'),  # Registration
    # Post-login landing page
    path('dashboard/', views.role_landing, name='role_landing'),
    path('profile/', views.profile_view, name='profile'),
    path('user_search/', views.user_search, name='user_search'),
    # public profile page by user ID
    path('users/<int:user_id>/', views.public_profile, name='public_profile'),

    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change_form.html",
            success_url=reverse_lazy("accounts:password_change_done"),
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html",
        ),
        name="password_change_done",
    ),
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/read/<int:pk>/',
         views.mark_notification_read, name='mark_notification_read'),
]
