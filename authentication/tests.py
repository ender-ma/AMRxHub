from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import uuid
import re

CustomUser = get_user_model()

class AuthenticationTestCase(TestCase):
    """Test cases for authentication functionality"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up non-modified data for all test methods"""
        # Static data that won't be modified by tests
        cls.auth_page_url = reverse('authentication:auth_page')  # Main auth page
        cls.register_url = reverse('authentication:register')    # Registration endpoint
        cls.login_url = reverse('authentication:login')          # Login endpoint
        cls.logout_url = reverse('authentication:logout')
        cls.password_reset_url = reverse('authentication:password_reset')
        
    def setUp(self):
        """Set up data for each test method"""
        self.client = Client()
        
        # Create a test user with unique identifiers to avoid conflicts
        unique_id = uuid.uuid4().hex[:8]
        self.test_user = CustomUser.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'testuser_{unique_id}@example.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='User',
            institution='Test University',
            status='student'
        )
        
        # Store credentials for later use
        self.user_credentials = {
            'username': self.test_user.username,
            'email': self.test_user.email,
            'password': 'TestPassword123!'
        }
    
    def test_user_registration(self):
        """Test user registration functionality"""
        # Generate unique user data for this test
        unique_id = uuid.uuid4().hex[:8]
        username = f'newuser_{unique_id}'
        email = f'newuser_{unique_id}@example.com'
        
        # Get the auth page (which contains the registration form)
        response = self.client.get(self.auth_page_url)
        self.assertEqual(response.status_code, 200)
        
        # Submit registration with data matching your template
        form_data = {
            'username': username,
            'email': email,
            'password': 'NewPassword123!',            # Not password1
            'confirm_password': 'NewPassword123!',    # Not password2
            'first_name': 'New',
            'last_name': 'User',
            'institution': 'Test University',
            'status': 'student',
            'agree_terms': 'on',  # Checkbox value
            'signup': 'Sign Up'   # Button name from template
        }
        
        response = self.client.post(
            self.register_url,  # Post to register endpoint
            form_data,
            follow=True
        )
        
        # Check if user was created
        self.assertTrue(
            CustomUser.objects.filter(username=username).exists(),
            f"User {username} was not created. Response: {response.status_code}"
        )
    
    def test_user_login(self):
        """Test user login functionality"""
        # Get auth page (contains login form)
        response = self.client.get(self.auth_page_url)
        self.assertEqual(response.status_code, 200)
        
        # Try invalid login
        response = self.client.post(
            self.login_url,
            {
                'username': self.test_user.username, 
                'password': 'WrongPassword123!',
                'login': 'Login'  # Button name from template
            },
            follow=True
        )
        # After failed login, should redirect back to auth page
        self.assertEqual(response.status_code, 200)
        
        # Try valid login
        response = self.client.post(
            self.login_url,
            {
                'username': self.test_user.username, 
                'password': 'TestPassword123!',
                'login': 'Login'
            },
            follow=True
        )
        # After successful login, should redirect to home
        self.assertEqual(response.status_code, 200)
        # Check user is authenticated
        user = response.context['user']
        self.assertTrue(user.is_authenticated)
    
    def test_user_logout(self):
        """Test user logout functionality"""
        # First login
        self.client.login(username=self.test_user.username, password='TestPassword123!')
        
        # Then logout
        response = self.client.post(self.logout_url, follow=True)
        
        # Check user is logged out
        self.assertFalse(response.context['user'].is_authenticated)
    
    def test_password_reset_flow(self):
        """Test the password reset flow"""
        # Request password reset
        response = self.client.post(
            self.password_reset_url,
            {'email': self.test_user.email},
            follow=True
        )
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password Reset for AMR Tool House')
        
        # Generate reset URL components directly rather than parsing email
        uid = urlsafe_base64_encode(force_bytes(self.test_user.pk))
        token = default_token_generator.make_token(self.test_user)
        
        # Construct the reset URL
        reset_path = reverse(
            'authentication:password_reset_confirm', 
            kwargs={'uidb64': uid, 'token': token}
        )
        
        # Visit the reset URL (which includes a redirect to the form)
        response = self.client.get(reset_path, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Get the form URL from the redirect chain
        reset_confirm_url = response.redirect_chain[-1][0]
        
        # Submit new password
        response = self.client.post(
            reset_confirm_url,
            {
                'new_password1': 'NewTestPassword123!',
                'new_password2': 'NewTestPassword123!'
            },
            follow=True
        )
        
        # Try login with new password
        self.client.logout()
        login_successful = self.client.login(
            username=self.test_user.username, 
            password='NewTestPassword123!'
        )
        self.assertTrue(login_successful, "Could not login with new password")
    
    def test_email_verification(self):
        """Test email verification functionality"""
        # Create unique token for verification
        unique_id = uuid.uuid4().hex[:8]
        token = f"testtoken_{unique_id}"
        
        # Create unverified user with unique identifiers
        unverified_user = CustomUser.objects.create_user(
            username=f'unverified_{unique_id}',
            email=f'unverified_{unique_id}@example.com',
            password='Unverified123!',
            first_name='Unverified',
            last_name='User',
            institution='Test University',
            status='student',
            is_email_verified=False,
            email_verification_token=token
        )
        
        # Visit verification URL
        verification_url = reverse('authentication:verify_email', args=[token])
        response = self.client.get(verification_url, follow=True)
        
        # Refresh user from database
        unverified_user.refresh_from_db()
        
        # Check user is now verified
        self.assertTrue(
            unverified_user.is_email_verified, 
            "User email was not marked as verified"
        )
        self.assertIsNone(
            unverified_user.email_verification_token,
            "Verification token was not cleared"
        )

## Running the Tests

'''To run these tests, use the following command:

```
python manage.py test authentication
```

These tests cover the core functionality of your authentication system:
- User registration with validation
- Login and logout processes
- Password reset email delivery and token validation
- Email verification token handling

You might need to adjust some details to match your exact implementation, especially:
- Form field names
- URL patterns
- Success/failure message text

These tests will help ensure your authentication system remains secure and functional as you continue
'''