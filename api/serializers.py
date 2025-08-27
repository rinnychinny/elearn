from django.contrib.auth.models import User
from rest_framework import serializers
from accounts.models import User, UserProfile
from courses.models import Course, Enrollment, Material


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


class CoursePublicSerializer(serializers.ModelSerializer):
    teacher = UserPublicSerializer(read_only=True)  # public profile only

    class Meta:
        model = Course
        fields = ["id", "title", "description", "teacher"]


class EnrollmentStudentCourseSerializer(serializers.ModelSerializer):
    """show course info for the current student."""
    course = CoursePublicSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "course"]


class CoursePublicSerializer(serializers.ModelSerializer):
    creator = UserPublicSerializer(read_only=True)
    collaborators = UserPublicSerializer(many=True, read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    feedback_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id", "title", "description",
            "creator", "collaborators",
            "average_rating", "feedback_count",
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CoursePublicSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        source="course", queryset=Course.objects.all(), write_only=True
    )

    class Meta:
        model = Enrollment
        fields = ["id", "course", "course_id", "blocked", "enrolled_at"]
        # student can’t set blocked
        read_only_fields = ["blocked", "enrolled_at"]


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ["id", "course", "title", "order", "content"]
