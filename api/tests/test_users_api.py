import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_public_list_exposes_only_safe_fields(create_user):
    u1 = create_user("teacher1", public_name="Dr. Smith",
                     public_status="Office hours", public_bio="Lecturer")
    u2 = create_user("student1", public_name="Alice",
                     public_status="Busy revising", public_bio="Second year")

    client = APIClient()
    client.force_authenticate(user=u1)

    resp = client.get("/api/users/")
    assert resp.status_code == 200
    data = resp.json()
    if isinstance(data, dict) and "results" in data:
        data = data["results"]

    # At least two users
    assert any(item["profile"]["public_name"] == "Alice" for item in data)
    # Ensure sensitive fields are NOT exposed
    for item in data:
        assert "username" not in item
        assert "email" not in item


@pytest.mark.django_db
def test_me_endpoint_returns_private_fields(create_user):
    user = create_user(
        "alice",
        public_name="Alice",
        public_status="Busy revising",
        public_bio="Second year student"
    )
    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.get("/api/users/me/")
    assert resp.status_code == 200
    data = resp.json()

    # check private fields are indeed here
    assert data["username"] == "alice"
    assert "email" in data
    assert "profile" in data
    assert data["profile"]["public_name"] == "Alice"


@pytest.mark.django_db
def test_me_endpoint_patch_updates_profile(create_user):
    user = create_user("bob", public_name="Bob",
                       public_status="old", public_bio="old bio")
    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.patch("/api/users/me/", {
        "first_name": "Bobby",
        "profile": {"public_status": "new status", "public_bio": "new bio"}
    }, format="json")

    assert resp.status_code == 200
    data = resp.json()
    assert data["first_name"] == "Bobby"
    assert data["profile"]["public_status"] == "new status"

    # Reload from DB to double-check
    user.refresh_from_db()
    assert user.first_name == "Bobby"
    assert user.profile.public_status == "new status"
    assert user.profile.public_bio == "new bio"
