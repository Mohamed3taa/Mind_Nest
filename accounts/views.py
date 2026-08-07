"""
accounts/views.py
-----------------
Handles all authentication and user profile logic:
- Register, Login, Logout
- Profile update (user info + avatar)
- Password change
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm, CustomPasswordChangeForm


def register_view(request):
    """
    Handle new user registration.
    On success: create user + auto-login + redirect to dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created.')
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Please fix the errors below.')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handle user login with username/password.
    Supports ?next= redirect after successful login.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'dashboard:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Log out the current user and redirect to login page."""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """
    Display and update user profile.
    Handles both User model fields and Profile model fields (avatar, bio, phone).
    Uses two forms simultaneously: UpdateUserForm + UpdateProfileForm.
    """
    user_form    = UpdateUserForm(instance=request.user)
    profile_form = UpdateProfileForm(instance=request.user.profile)

    if request.method == 'POST':
        user_form    = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please fix the errors below.')

    context = {
        'user_form':    user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password_view(request):
    """
    Allow logged-in user to change their password.
    Calls update_session_auth_hash to keep the user logged in after change.
    """
    form = CustomPasswordChangeForm(request.user, request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)   # prevent logout after password change
            messages.success(request, 'Password changed successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please fix the errors below.')

    return render(request, 'accounts/change_password.html', {'form': form})
