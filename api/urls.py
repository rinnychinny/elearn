from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CourseViewSet, EnrollmentViewSet

from django.urls import path
from django.views.generic import TemplateView

app_name = 'api'

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")

urlpatterns = router.urls + [
    path("about/", TemplateView.as_view(template_name="api/api-about.html"),
         name="api-about"),
]
