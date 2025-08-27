import pytest
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment, Material

User = get_user_model()

# Tests: Public course list / detail ----------


@pytest.mark.django_db
def test_public_course_list(api, create_user, course_factory):
    user = create_user("any", public_name="Any")
    api.force_authenticate(user=user)

    course_factory("Django 101")
    course_factory("Web Sockets")

    resp = api.get("/api/courses/")
    assert resp.status_code == 200
    items = resp.json()
    titles = {it["title"] for it in items}
    assert {"Django 101", "Web Sockets"} <= titles

    first = items[0]
    assert "username" not in first["creator"]
    assert "email" not in first["creator"]
    assert "profile" in first["creator"]
    assert "public_name" in first["creator"]["profile"]


@pytest.mark.django_db
def test_public_course_detail(api, create_user, course_factory):
    user = create_user("any", public_name="Any")
    api.force_authenticate(user=user)

    course = course_factory("Async Python", description="Learn async")
    resp = api.get(f"/api/courses/{course.id}/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Async Python"
    assert data["description"] == "Learn async"
    assert data["creator"]["profile"]["public_name"].endswith("Teacher")


# ---------- Tests: Students roster (teacher-only) ----------

@pytest.mark.django_db
def test_teacher_can_view_roster(api, create_user, course_factory):
    teacher = create_user("t1", public_name="Dr. T")
    course = course_factory("Django 201", creator=teacher)

    s1 = create_user("alice", public_name="Alice")
    s2 = create_user("bob", public_name="Bob")
    Enrollment.objects.create(user=s1, course=course)
    Enrollment.objects.create(user=s2, course=course)

    api.force_authenticate(user=teacher)
    resp = api.get(f"/api/courses/{course.id}/students/")
    assert resp.status_code == 200
    data = resp.json()
    names = {u["profile"]["public_name"] for u in data}
    assert {"Alice", "Bob"} <= names


@pytest.mark.django_db
def test_non_teacher_cannot_view_roster(api, create_user, course_factory):
    teacher = create_user("t2", public_name="Dr. T2")
    course = course_factory("DRF 101", creator=teacher)
    student = create_user("charlie", public_name="Charlie")
    Enrollment.objects.create(user=student, course=course)

    other = create_user("eve", public_name="Eve")
    api.force_authenticate(user=other)
    resp = api.get(f"/api/courses/{course.id}/students/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_teacher_can_toggle_include_blocked_on_roster(api, create_user, course_factory):
    teacher = create_user("t3", public_name="Prof T3")
    course = course_factory("Security 101", creator=teacher)
    s1 = create_user("nina", public_name="Nina")
    s2 = create_user("omar", public_name="Omar")

    Enrollment.objects.create(user=s1, course=course, blocked=False)
    Enrollment.objects.create(user=s2, course=course, blocked=True)

    api.force_authenticate(user=teacher)

    resp = api.get(f"/api/courses/{course.id}/students/")
    names = {u["profile"]["public_name"] for u in resp.json()}
    assert "Nina" in names and "Omar" not in names

    resp2 = api.get(f"/api/courses/{course.id}/students/?include_blocked=true")
    names2 = {u["profile"]["public_name"] for u in resp2.json()}
    assert {"Nina", "Omar"} <= names2


# ---------- Tests: Materials access ----------

@pytest.mark.django_db
def test_teacher_can_view_materials(api, create_user, course_factory):
    teacher = create_user("t4", public_name="Dr. Mat")
    course = course_factory("Algorithms", creator=teacher)
    Material.objects.create(course=course, title="Syllabus", order=1)
    Material.objects.create(course=course, title="Lecture 1", order=2)

    api.force_authenticate(user=teacher)
    resp = api.get(f"/api/courses/{course.id}/materials/")
    assert resp.status_code == 200
    titles = [m["title"] for m in resp.json()]
    assert titles == ["Syllabus", "Lecture 1"]


@pytest.mark.django_db
def test_enrolled_student_can_view_materials(api, create_user, course_factory):
    teacher = create_user("t5", public_name="T5")
    course = course_factory("Networks", creator=teacher)
    Material.objects.create(course=course, title="Week 1", order=1)
    student = create_user("stu1", public_name="Stu One")
    Enrollment.objects.create(user=student, course=course, blocked=False)

    api.force_authenticate(user=student)
    resp = api.get(f"/api/courses/{course.id}/materials/")
    assert resp.status_code == 200
    data = resp.json()
    assert [m["title"] for m in data] == ["Week 1"]


@pytest.mark.django_db
def test_blocked_student_cannot_view_materials(api, create_user, course_factory):
    teacher = create_user("t6", public_name="T6")
    course = course_factory("Databases", creator=teacher)
    Material.objects.create(course=course, title="ER Models", order=1)
    student = create_user("stu2", public_name="Stu Two")
    Enrollment.objects.create(user=student, course=course, blocked=True)

    api.force_authenticate(user=student)
    resp = api.get(f"/api/courses/{course.id}/materials/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_non_enrolled_student_cannot_view_materials(api, create_user, course_factory):
    teacher = create_user("t7", public_name="T7")
    course = course_factory("Compilers", creator=teacher)
    Material.objects.create(course=course, title="Parsing", order=1)
    stranger = create_user("stranger", public_name="Visitor")

    api.force_authenticate(user=stranger)
    resp = api.get(f"/api/courses/{course.id}/materials/")
    assert resp.status_code == 403


# ---------- Tests: course aggregation ----------

@pytest.mark.django_db
def test_my_courses_returns_teaching_and_enrolled(api, create_user, course_factory):
    teacher = create_user("teachA", public_name="Teach A")
    c1 = course_factory("C1", creator=teacher)
    c2 = course_factory("C2")
    c2.collaborators.add(teacher)

    c3 = course_factory("C3")
    Enrollment.objects.create(user=teacher, course=c3, blocked=False)

    api.force_authenticate(user=teacher)
    resp = api.get("/api/users/me/courses/")
    assert resp.status_code == 200
    payload = resp.json()

    teaching_titles = {c["title"] for c in payload["teaching"]}
    enrolled_titles = {c["title"] for c in payload["enrolled"]}

    assert {"C1", "C2"} <= teaching_titles
    assert {"C3"} <= enrolled_titles
