from django.contrib.auth.models import User
from rest_framework import serializers
from accounts.models import User, UserProfile


class UserProfilePublicSerializer(serializers.ModelSerializer):
    """public-facing fields."""
    class Meta:
        model = UserProfile
        fields = ["public_name", "public_status", "public_bio"]


class UserPublicSerializer(serializers.ModelSerializer):
    """just an ID + profile."""
    profile = UserProfilePublicSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "profile"]  # no username for security reasons


class UserMeSerializer(serializers.ModelSerializer):
    """Full info for the logged-in user"""
    profile = UserProfilePublicSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "email",
                  "first_name", "last_name", "profile"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)
        instance = super().update(instance, validated_data)

        if profile_data:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            for field, value in profile_data.items():
                setattr(profile, field, value)
            profile.save()

        return instance
