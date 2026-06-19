from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'authentication'

urlpatterns = [
    # Main authentication page (redirects to login)
    path('', views.auth_page, name='auth_page'),
    
    # Separate login and signup URLs
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    
    # Existing authentication endpoints
    path('login-submit/', views.login_user, name='login_submit'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    
    # Password reset functionality
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
    
    # Other endpoints
    path('change-password/', views.change_password_view, name='change_password'),
    path('terms/', views.terms_view, name='terms'),
    path('check-email/', views.check_email_availability, name='check_email'),
    path('debug/', views.debug_auth, name='debug_auth'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('google/login/', views.google_login, name='google_login'),
    path('test-email/', views.test_email, name='test_email'),

    # Email verification functionality
    path("verify-email/<uidb64>/<token>/", views.verify_email_view, name="verify_email"),
    path("send-verification-email/", views.resend_verification_email, name="send_verification_email"),

]
