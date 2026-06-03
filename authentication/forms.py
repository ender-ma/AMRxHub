from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for user creation with email-based authentication.
    """
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all fields have empty help_text
        for field in self.fields.values():
            field.help_text = ''
        
        # Add CSS classes for JavaScript targeting
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'id': 'id_email'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'id': 'id_first_name'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'id': 'id_last_name'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'id': 'id_password1'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'id': 'id_password2'})
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2

class SignupForm(CustomUserCreationForm):
    """Form for user signup with additional validation"""
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user
