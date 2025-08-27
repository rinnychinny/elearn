from rest_framework.permissions import BasePermission


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == "teacher"


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == "student"


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "user_id", None) == request.user.id or getattr(obj, "id", None) == request.user.id
