from django.urls import path
from .views import CourseCreateView, CourseListView, CourseDetailView, MaterialCreateView, MaterialDeleteView, MaterialMoveView, EnrollView, DisenrollView, FeedbackCreateView
from django.views.generic import RedirectView

app_name = 'courses'

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('create/', CourseCreateView.as_view(), name='course_create'),

    path(
        "<int:course_id>/",
        RedirectView.as_view(
            pattern_name="courses:course_detail_section", permanent=False
        ),
        {"section": "materials"},
        name="course_detail",
    ),
    path("<int:course_id>/feedback/new/", FeedbackCreateView.as_view(),
         name="course_feedback_create"),
    path('<int:course_id>/enroll/',
         EnrollView.as_view(), name='enroll'),
    path('<int:course_id>/disenroll/',
         DisenrollView.as_view(), name='disenroll'),

    path("<int:course_id>/<slug:section>/",
         CourseDetailView.as_view(), name="course_detail_section"),

    path('<int:course_id>/materials/add/',
         MaterialCreateView.as_view(), name='material_create'),
    path('materials/<int:material_id>/delete/',
         MaterialDeleteView.as_view(), name='material_delete'),
    path('materials/<int:material_id>/move/<str:direction>/',
         MaterialMoveView.as_view(), name='move_material'),



]
