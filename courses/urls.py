from django.urls import path
from .views import CourseCreateView, CourseListView, CourseDetailView, MaterialCreateView

app_name = 'courses'

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('create/', CourseCreateView.as_view(), name='course_create'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course_detail'), 
    path('<int:course_id>/materials/add/', MaterialCreateView.as_view(), name='material_create'),
]
