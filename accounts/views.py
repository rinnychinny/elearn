from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash


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
def profile_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user, defaults={'public_name': user.username})
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'accounts/profile_page.html', {'profile_form': form})

@login_required
def role_landing(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user, defaults={'public_name': user.username})
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('role_landing')
    else:
        form = UserProfileForm(instance=profile)
    
    roles = []
    if user.is_superuser or user.groups.filter(name='admin').exists():
        roles.append('admin')
    if user.groups.filter(name='teacher').exists():
        roles.append('teacher')
    if user.groups.filter(name='student').exists():
        roles.append('student')
    context = {'roles': roles, 'profile_form': form}
    return render(request, 'accounts/role_landing.html', context)


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('password_change_done')
    
    def form_valid(self, form):
        form.save()
        #Prevent user from getting logged out
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)

