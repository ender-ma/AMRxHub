from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from allauth.account.utils import perform_login
from profil.models import UserProfile

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a social provider,
        but before the login is actually processed.
        """
        # Get email from social account
        email = sociallogin.account.extra_data.get('email')
        
        # Check if already connected
        if sociallogin.is_existing:
            # User already has a social account
            return
            
        # Try to find matching user by email
        if email:
            try:
                user = User.objects.get(email=email)
                # Connect the social account to this existing user
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass
    
    def populate_user(self, request, sociallogin, data):
        """
        Populates user information from social provider data
        """
        user = sociallogin.user
        
        # Ensure email is set
        user.email = data.get('email', '')
        
        # Get name information from Google
        if sociallogin.account.provider == 'google':
            user.first_name = data.get('given_name', '')
            user.last_name = data.get('family_name', '')
        
        # Set username if the field exists (though we're using email as primary identifier)
        if hasattr(user, 'username') and not user.username:
            # Create a valid username
            base_username = user.email.split('@')[0]
            username = base_username[:30]  # Respect length limit
            user.username = username
            
        return user
            
    def save_user(self, request, sociallogin, form=None):
        """
        Overriding the save_user method to create profile after user creation
        """
        user = super().save_user(request, sociallogin, form)
        
        # Make sure name fields are populated from Google data
        if sociallogin.account.provider == 'google':
            first_name = sociallogin.account.extra_data.get('given_name', '')
            last_name = sociallogin.account.extra_data.get('family_name', '')
            
            if first_name and not user.first_name:
                user.first_name = first_name
            if last_name and not user.last_name:
                user.last_name = last_name
        
        # Ensure username is set if the field exists
        if hasattr(user, 'username') and not user.username:
            user.username = user.email.split('@')[0][:30]
            
        user.is_email_verified = True  # Google provides verified emails
        user.save()
        
        # Create or update user profile
        try:
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                profile.save()
        except Exception as e:
            print(f"Error creating profile: {e}")
            
        return user