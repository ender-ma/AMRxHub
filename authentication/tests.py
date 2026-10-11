from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import email_verification_token

User = get_user_model()
PASSWORD = 'TestPassword123!'


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='member@example.com', password=PASSWORD, first_name='Test', last_name='User',
        )

    def test_registration_creates_user_signs_in_and_sends_welcome_email(self):
        response = self.client.post(reverse('authentication:register'), {
            'email': 'New.User@Example.com',
            'password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!',
            'first_name': 'New',
            'last_name': 'User',
        })
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)
        self.assertTrue(User.objects.filter(email='new.user@example.com').exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(int(self.client.session['_auth_user_id']), User.objects.get(email='new.user@example.com').pk)

    def test_registration_rejects_mismatched_passwords_and_duplicate_email(self):
        base = {'password': 'NewPassword123!', 'first_name': 'A', 'last_name': 'B'}
        self.client.post(reverse('authentication:register'),
                         {**base, 'email': 'other@example.com', 'confirm_password': 'Different123!'})
        self.client.post(reverse('authentication:register'),
                         {**base, 'email': 'MEMBER@example.com', 'confirm_password': 'NewPassword123!'})
        self.assertEqual(User.objects.count(), 1)

    def test_login_with_wrong_and_right_password(self):
        url = reverse('authentication:login_submit')
        self.client.post(url, {'email': self.user.email, 'password': 'wrong-password'})
        self.assertNotIn('_auth_user_id', self.client.session)

        response = self.client.post(url, {'email': self.user.email, 'password': PASSWORD})
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_logout(self):
        self.client.force_login(self.user)
        self.client.post(reverse('authentication:logout'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_password_reset_flow(self):
        self.client.post(reverse('authentication:password_reset'), {'email': self.user.email})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        response = self.client.post(
            reverse('authentication:password_reset_confirm', args=[uid, token]),
            {'new_password1': 'BrandNewPass456!', 'new_password2': 'BrandNewPass456!'},
        )
        self.assertRedirects(response, reverse('authentication:login'), fetch_redirect_response=False)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('BrandNewPass456!'))

    def test_password_reset_for_unknown_email_sends_nothing(self):
        self.client.post(reverse('authentication:password_reset'), {'email': 'nobody@example.com'})
        self.assertEqual(len(mail.outbox), 0)

    def test_email_verification_link(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.client.get(reverse('authentication:verify_email', args=[uid, 'bad-token']))
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_email_verified)

        token = email_verification_token.make_token(self.user)
        self.client.get(reverse('authentication:verify_email', args=[uid, token]))
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)
