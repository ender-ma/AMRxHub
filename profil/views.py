from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PersonalInfoForm, ResearchInfoForm, AccountSettingsForm
from .models import UserProfile, ResearchInterest
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()

@login_required
def profile_view(request):
    """Main profile view that shows all sections"""
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    

    try:
        # Forms for each section
        personal_form = PersonalInfoForm(instance=profile, user=request.user)
        research_form = ResearchInfoForm(instance=profile)
        settings_form = AccountSettingsForm(instance=profile)
        password_form = PasswordChangeForm(request.user)
        
        # Get available research interests for the template
        all_interests = ResearchInterest.objects.all()
        # print(f"Research interests: {all_interests.count()} interests found")
        
    except Exception as e:
        print(f"Error creating forms: {e}")
        messages.error(request, f"Error loading profile data: {e}")
        return redirect('home')
    
    context = {
        'personal_form': personal_form,
        'research_form': research_form,
        'settings_form': settings_form,
        'password_form': password_form,
        'profile': profile,
        'all_interests': all_interests,
    }
    
    return render(request, 'profil/profile.html', context)

@login_required
def update_personal_info(request):
    """Handle personal information updates"""
    if request.method == 'POST':
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Enhanced debug info
        print(f"Received POST data: {request.POST}")
        print(f"Profile before update: {profile.department}, {profile.role}, {profile.organization}, {profile.country}")
        
        form = PersonalInfoForm(request.POST, instance=profile, user=request.user)
        
        if form.is_valid():
            # Save profile changes
            profile = form.save()
            
            # Update user info (first_name, last_name)
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.save()
            
            print(f"Profile after update: {profile.department}, {profile.role}, {profile.organization}, {profile.country}")
            print(f"User after update: {user.first_name} {user.last_name}")
            
            messages.success(request, "Personal information updated successfully!")
        else:
            print(f"Form validation failed: {form.errors}")
            messages.error(request, f"Error updating profile: {form.errors}")
            print(f"Form errors: {form.errors}")
    
    # Redirect back to profile page
    return redirect('profil:profile')

@login_required
def update_research_info(request):
    """Handle research information updates"""
    if request.method == 'POST':
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        form = ResearchInfoForm(request.POST, instance=profile)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Research information updated successfully.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    return redirect('profil:profile')

@login_required
def update_account_settings(request):
    """Handle account settings updates"""
    if request.method == 'POST':
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        form = AccountSettingsForm(request.POST, instance=profile)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Account settings updated successfully.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    return redirect('profil:profile')

@login_required
def change_password(request):
    """Handle password changes"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Your password was successfully updated!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    return redirect('profil:profile')

@login_required
def delete_account(request):
    """Handle account deletion with email verification"""
    if request.method == 'POST':
        # This would normally include email verification
        # For now, just display a message
        messages.warning(request, 'Account deletion requires email verification. This feature is coming soon.')
    
    return redirect('profil:profile')

@login_required
def transfer_account(request):
    """Handle account transfer with email verification"""
    if request.method == 'POST':
        # This would normally include email verification
        # For now, just display a message
        messages.warning(request, 'Account transfer requires email verification. This feature is coming soon.')
    
    return redirect('profil:profile')