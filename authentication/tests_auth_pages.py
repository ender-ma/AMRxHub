from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    GOOGLE_CLIENT_ID="",
    GOOGLE_CLIENT_SECRET="",
)
class AuthenticationPageTests(TestCase):
    def test_login_and_signup_pages_render_with_csrf_cookie(self):
        for url_name in ("authentication:login", "authentication:signup"):
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200)
            self.assertIn("csrftoken", response.cookies)

    def test_email_login_accepts_valid_credentials(self):
        User = get_user_model()
        email = "login-test@example.com"
        password = "TestPassword123!"
        User.objects.create_user(
            email=email,
            password=password,
            first_name="Login",
            last_name="Test",
        )

        response = self.client.post(
            reverse("authentication:login"),
            {"email": email, "password": password},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")

    def test_google_login_without_oauth_config_redirects_to_login(self):
        response = self.client.get(reverse("authentication:google_login"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("authentication:login"))

    @override_settings(GOOGLE_CLIENT_ID="fake-client", GOOGLE_CLIENT_SECRET="fake-secret")
    def test_google_login_with_oauth_config_redirects_to_allauth(self):
        response = self.client.get(
            reverse("authentication:google_login"),
            {"process": "login", "next": "/"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            "/accounts/google/login/?process=login&next=%2F",
        )
