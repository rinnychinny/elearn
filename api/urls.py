from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CourseViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")

urlpatterns = router.urls
