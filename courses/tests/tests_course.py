import pytest
from django.urls import reverse
from django.contrib.auth.models import Group
from django.test import Client
from courses.models import Course, Enrollment, Material


@pytest.fixture
def teacher_user(django_user_model):
    user = django_user_model.objects.create_user(
        username='teacher', password='pass')
    teacher_group, _ = Group.objects.get_or_create(name='teacher')
    user.groups.add(teacher_group)
    return user


@pytest.fixture
def student_user(django_user_model):
    return django_user_model.objects.create_user(username='student', password='pass')


@pytest.fixture
def course(teacher_user):
    return Course.objects.create(title="Test Course", creator=teacher_user)


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
def test_course_create_view_permission(client, teacher_user, student_user):
    # Teacher can access course creation page
    client.login(username='teacher', password='pass')
    url = reverse('courses:course_create')
    response = client.get(url)
    assert response.status_code == 200

    # Student cannot access course creation page
    client.logout()
    client.login(username='student', password='pass')
    response = client.get(url)
    assert response.status_code == 403 or response.status_code == 302


@pytest.mark.django_db
def test_course_list_view_context(client, student_user, course):
    client.login(username='student', password='pass')
    url = reverse('courses:course_list')
    response = client.get(url)
    assert response.status_code == 200
    # The context should have keys for enrolled_courses, all_courses, etc.
    context = response.context
    assert 'enrolled_courses' in context
    assert 'all_courses' in context
    assert 'created_courses' in context
    assert 'collaborating_courses' in context


@pytest.mark.django_db
def test_enroll_view(client, student_user, course):
    client.login(username='student', password='pass')
    url = reverse('courses:enroll', kwargs={'course_id': course.id})
    response = client.post(url)
    assert response.status_code == 302  # Redirect after enrollment
    assert course.enrolled_users.filter(id=student_user.id).exists()


@pytest.mark.django_db
def test_course_detail_redirect(client, student_user, course):
    client.login(username='student', password='pass')
    url = reverse('courses:course_detail', kwargs={
                  'course_id': course.id})  # no section param
    response = client.get(url)
    assert response.status_code == 302
    # redirected to default section URL
    assert response.url.endswith('/materials/')


@pytest.mark.django_db
def test_material_create_view_permission(client, teacher_user, student_user, course):
    url = reverse('courses:material_create', kwargs={'course_id': course.id})

    client.login(username='student', password='pass')
    response = client.get(url)
    # Denied for non-teacher
    assert response.status_code == 403 or response.status_code == 302

    client.logout()
    client.login(username='teacher', password='pass')
    response = client.get(url)
    assert response.status_code == 200

# Add other view tests similarly for DisenrollView, FeedbackCreateView, BlockStudentView, etc.
