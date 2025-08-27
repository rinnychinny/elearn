# api/tests/conftest.py
from django.test.utils import override_settings
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from courses.models import Course

User = get_user_model()


@pytest.fixture
def api():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture(autouse=True)
def no_pagination():
    with override_settings(REST_FRAMEWORK={"DEFAULT_PAGINATION_CLASS": None}):
        yield


@pytest.fixture
def create_user(db):
    """
    Create a User. A UserProfile is assumed to be auto-created by a signal.
    Any extra kwargs are applied to the existing profile (NOT created).
    Usage:
        user = create_user("alice", public_name="Alice", public_status="Busy", public_bio="CS student")
    """
    def make_user(username, password="pass123", is_staff=False, is_superuser=False, **profile_fields):
        user = User.objects.create_user(
            username=username,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        profile = getattr(user, "profile", None)
        if profile is None:
            # If profile not created, fail
            raise RuntimeError(
                "Expected UserProfile to be created by signal, but none found.")

        # Apply provided public fields to the existing profile
        for field, value in profile_fields.items():
            setattr(profile, field, value)
        profile.save()

        return user

    return make_user


@pytest.fixture
def course_factory(db, create_user):
    def make(title, creator=None, description="desc"):
        creator = creator or create_user(
            f"creator_{title}", public_name=f"{title} Teacher")
        c = Course.objects.create(
            title=title, description=description, creator=creator)
        return c
    return make
