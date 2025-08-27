from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import UserPublicSerializer, UserMeSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    - /api/users/       → list of users (public fields only)
    - /api/users/<id>/  → single user (public fields only)
    - /api/users/me/    → full detail for current user, incl. update
    """
    queryset = User.objects.select_related("profile")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return UserPublicSerializer  # default is public data

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        if request.method == "GET":
            serializer = UserMeSerializer(request.user)
            return Response(serializer.data)
        elif request.method == "PATCH":
            serializer = UserMeSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # refetch to ensure updated object info
            fresh = User.objects.select_related(
                "profile").get(pk=request.user.pk)
            return Response(UserMeSerializer(fresh).data)
