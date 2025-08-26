from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth import login
from django.shortcuts import render, redirect

from .forms import UserProfileForm
from .models import UserProfile


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
def user_search(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        # Search public_name
        results = UserProfile.objects.filter(
            public_name__icontains=query).select_related('user')
        for profile in results:
            user_groups = profile.user.groups.values_list('name', flat=True)
            profile.user_groups_csv = ", ".join(user_groups)
            profile.is_teacher = 'Teacher' in user_groups
            profile.is_student = 'Student' in user_groups

    context = {
        "query": query,
        "results": results,
    }
    return render(request, "accounts/user_search.html", context)


@login_required
def profile_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(
        user=user, defaults={'public_name': user.username})
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'accounts/profile_page.html', {'profile_form': form})


@login_required
def public_profile(request, user_id):
    profile = get_object_or_404(UserProfile, user__id=user_id)
    user_groups = profile.user.groups.values_list('name', flat=True)
    profile.user_groups_csv = ", ".join(user_groups)
    profile.is_teacher = 'Teacher' in user_groups
    profile.is_student = 'Student' in user_groups
    return render(request, 'accounts/public_profile.html', {'profile': profile})


@login_required
def role_landing(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(
        user=user, defaults={'public_name': user.username})
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('role_landing')
    else:
        form = UserProfileForm(instance=profile)

    context = {'profile_form': form}
    return render(request, 'accounts/role_landing.html', context)
