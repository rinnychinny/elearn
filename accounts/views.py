from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth import login
from django.shortcuts import render, redirect


def student_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Add to student group automatically
            student_group = Group.objects.get(name='student')
            user.groups.add(student_group)
            login(request, user)  # Log in immediately after registration
            return redirect('role_landing')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def role_landing(request):
    user = request.user
    roles = []
    if user.is_superuser or user.groups.filter(name='admin').exists():
        roles.append('admin')
    if user.groups.filter(name='teacher').exists():
        roles.append('teacher')
    if user.groups.filter(name='student').exists():
        roles.append('student')
    return render(request, 'accounts/role_landing.html', {'roles': roles})
