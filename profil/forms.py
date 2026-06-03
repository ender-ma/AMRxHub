from django import forms
from .models import UserProfile, ResearchInterest

class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['department', 'role', 'organization', 'country']
        labels = {
            'department': 'Department',
            'role': 'Role',
            'organization': 'Organization/Institution',
            'country': 'Country',
        }
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control'}),  # Changed from Select to TextInput
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract the user from kwargs before calling super
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
       
class ResearchInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # Update to use 'interests' instead of 'research_interests'
        fields = ['interests', 'research_background']
        labels = {
            'interests': 'Research Interests',
            'research_background': 'Research Background',
        }
        widgets = {
            'interests': forms.CheckboxSelectMultiple(),
            'research_background': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['receive_research_updates', 'receive_email_notifications', 'profile_visibility']
        labels = {
            'receive_research_updates': 'Receive Research Updates',
            'receive_email_notifications': 'Receive Email Notifications',
            'profile_visibility': 'Profile Visibility',
        }