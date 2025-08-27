# api/views.py
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from courses.models import Course, Enrollment, Material
from .serializers import (CoursePublicSerializer,
                          EnrollmentSerializer,
                          MaterialSerializer,
                          UserPublicSerializer,
                          UserMeSerializer)
from .utils import is_course_teacher


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public: list/retrieve courses.
    Extra (teachers only): /api/courses/{id}/students/?include_blocked=true|false
    Materials: visible to course teachers, or enrolled (non-blocked) users.
    """
    queryset = (
        Course.objects
        .select_related("creator", "creator__profile")
        .prefetch_related("collaborators", "collaborators__profile")
    )
    serializer_class = CoursePublicSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["get"], url_path="students")
    def students(self, request, pk=None):
        course = self.get_object()
        if not is_course_teacher(request.user, course):
            return Response({"detail": "Forbidden"}, status=403)

        include_blocked = request.query_params.get(
            "include_blocked", "false").lower() == "true"
        enr_qs = Enrollment.objects.filter(course=course)
        if not include_blocked:
            enr_qs = enr_qs.filter(blocked=False)

        user_ids = list(enr_qs.values_list("user_id", flat=True))
        users = User.objects.filter(id__in=user_ids).select_related("profile")
        return Response(UserPublicSerializer(users, many=True).data)

    @action(detail=True, methods=["get"], url_path="materials")
    def materials(self, request, pk=None):
        course = self.get_object()
        teacher_ok = is_course_teacher(request.user, course)
        enrolled_ok = Enrollment.objects.filter(
            course=course, user=request.user, blocked=False
        ).exists()
        if not (teacher_ok or enrolled_ok):
            return Response({"detail": "Forbidden"}, status=403)

        mats = course.materials.all().order_by("order", "id")
        return Response(MaterialSerializer(mats, many=True).data)


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    Optional endpoints to enroll/unenroll and manage 'blocked'.
    - Student: can create/delete only own enrollment; cannot set 'blocked'.
    - Teacher (creator/collaborator): can view all enrollments for their course,
      and PATCH 'blocked' for users on their course; can delete any enrollment on their course.
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        u = self.request.user
        # Students -> their own enrollments
        # Teachers -> enrollments on courses they teach
        return Enrollment.objects.select_related(
            "course", "course__creator", "course__creator__profile"
        ).prefetch_related(
            "course__collaborators", "course__collaborators__profile"
        ).filter(
            Q(user=u) |
            Q(course__creator=u) |
            Q(course__collaborators=u)
        ).distinct()

    def perform_create(self, serializer):
        # Self-enroll only; teachers can enroll themselves too (fine).
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        # Allow teachers to PATCH 'blocked' for enrollments on their course.
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if not is_course_teacher(request.user, instance.course):
            # Students can’t update an enrollment (only delete their own)
            return Response({"detail": "Forbidden"}, status=403)

        # Only allow 'blocked' to be updated by teachers
        allowed = {}
        if "blocked" in request.data:
            allowed["blocked"] = bool(request.data["blocked"])

        if not allowed:
            return Response({"detail": "No updatable fields."}, status=400)

        for k, v in allowed.items():
            setattr(instance, k, v)
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Student can drop own enrollment; teacher can remove anyone from their course
        if instance.user_id != request.user.id and not is_course_teacher(request.user, instance.course):
            return Response({"detail": "Forbidden"}, status=403)
        return super().destroy(request, *args, **kwargs)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    - /api/users/             -> public profile list
    - /api/users/<id>/        -> public profile detail
    - /api/users/me/          -> self profile GET/PATCH
    - /api/users/me/courses/  -> teaching & enrolled courses
    """
    queryset = User.objects.select_related("profile")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return UserPublicSerializer

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        if request.method == "GET":
            return Response(UserMeSerializer(request.user).data)
        ser = UserMeSerializer(request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        fresh = User.objects.select_related("profile").get(pk=request.user.pk)
        return Response(UserMeSerializer(fresh).data)

    @action(detail=False, methods=["get"], url_path="me/courses")
    def my_courses(self, request):
        u = request.user
        teaching = (
            Course.objects
            .filter(Q(creator=u) | Q(collaborators=u))
            .select_related("creator", "creator__profile")
            .prefetch_related("collaborators", "collaborators__profile")
            .distinct()
        )
        # via your M2M (through=Enrollment) with related_name="courses_enrolled"
        enrolled = (
            u.courses_enrolled
             .select_related("creator", "creator__profile")
             .prefetch_related("collaborators", "collaborators__profile")
             .all()
        )
        return Response({
            "teaching": CoursePublicSerializer(teaching, many=True).data,
            "enrolled": CoursePublicSerializer(enrolled, many=True).data,
        })
