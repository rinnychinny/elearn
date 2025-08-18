from django.urls import path
from .views import CourseCreateView, CourseListView, CourseDetailView, MaterialCreateView, MaterialDeleteView, MaterialMoveView, EnrollView, DisenrollView

app_name = 'courses'

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('create/', CourseCreateView.as_view(), name='course_create'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course_detail'), 
    path('<int:course_id>/materials/add/', MaterialCreateView.as_view(), name='material_create'),
    path('materials/<int:pk>/delete/', MaterialDeleteView.as_view(), name='material_delete'),
    path('materials/<int:material_id>/move/<str:direction>/', MaterialMoveView.as_view(), name='move_material'),
    path('courses/<int:course_id>/enroll/', EnrollView.as_view(), name='enroll'),
    path('courses/<int:course_id>/disenroll/', DisenrollView.as_view(), name='disenroll'),
]
