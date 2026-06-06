from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from .models import CustomUser
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.http import JsonResponse, HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
import logging
from .forms import CustomUserCreationForm, SignupForm
from django.db import transaction
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str 
from django.conf import settings
import os
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_POST
from .tokens import email_verification_token

# Set up logging
logger = logging.getLogger(__name__)

User = get_user_model()

def send_verification_email(request, user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    protocol = "https" if request.is_secure() else "http"
    domain = request.get_host()

    message = render_to_string("registration/verification_email.html", {
        "protocol": protocol,
        "domain": domain,
        "uidb64": uidb64,
        "token": token,
        "user": user,
    })

    send_mail(
        "Verify your AMRx Hub email",
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

def verify_email_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and email_verification_token.check_token(user, token):
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])
        messages.success(request, "Email verified successfully.")
        return redirect("authentication:login")

    messages.error(request, "Verification link is invalid or expired.")
    return redirect("authentication:login")

@login_required
@require_POST
def resend_verification_email(request):
    if request.user.is_email_verified:
        return JsonResponse({"success": True, "message": "Email already verified."})

    try:
        send_verification_email(request, request.user)
        return JsonResponse({"success": True, "message": "Verification email sent."})
    except Exception:
        return JsonResponse({"success": False, "message": "Could not send verification email."}, status=500)

@never_cache
@ensure_csrf_cookie
def auth_page(request):
    """Main authentication page with login/register forms"""
    logger.info(f"Auth page accessed by {request.META.get('REMOTE_ADDR')}")
    
    # if request.user.is_authenticated:
    #     messages.info(request, f'You are already logged in as {request.user.email}.')
    #     return redirect('home')
    
    return render(request, 'authentication/main_auth.html')

@never_cache
def register_user(request):
    """Handle user registration with email-based authentication"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        # Validation
        if not all([email, password, confirm_password, first_name, last_name]):
            messages.error(request, 'All fields are required.')
            return render(request, 'authentication/signup.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authentication/signup.html')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'authentication/signup.html')

        if CustomUser.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already registered. Please use another email.')
            return render(request, 'authentication/signup.html')

        try:
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            user.is_active = True
            user.save()

            # Create user profile
            from profil.models import UserProfile
            try:
                profile = UserProfile.objects.create(user=user)
                profile.save()
            except Exception as profile_error:
                logger.error(f'Profile creation error: {str(profile_error)}')

            # Auto-login user after registration
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                logger.warning(f'User created but auto-login failed: {email}')
                messages.success(request, 'Account created successfully! You can now log in.')
                return redirect('authentication:auth_page')

        except Exception as db_error:
            logger.error(f'Database error during user creation: {str(db_error)}')
            messages.error(request, 'Failed to create account. Please try again.')
            return render(request, 'authentication/signup.html')

    # GET request or any other method
    return render(request, 'authentication/signup.html')

@never_cache
def login_user(request):
    """Handle user login with email-based authentication"""
    if request.method == 'POST':
        try:
            email = request.POST.get('email', '').strip().lower()
            password = request.POST.get('password', '')
            
            if not email or not password:
                messages.error(request, 'Email and password are required.')
                return redirect('authentication:auth_page')
            
            # Print debugging information
            logger.info(f'Login attempt: {email}')
            
            # Authenticate with email
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                if user.is_active:
                    try:
                        login(request, user)
                        logger.info(f'User logged in: {email}')
                        messages.success(request, f'Welcome back, {user.get_full_name() or email}!')
                        
                        # Redirect to next page or home
                        next_page = request.POST.get('next') or request.GET.get('next')
                        if next_page and next_page.startswith('/'):
                            return redirect(next_page)
                        return redirect('home')
                    except Exception as login_error:
                        logger.error(f'Login process error: {str(login_error)}')
                        messages.error(request, f'Login failed: {str(login_error)}')
                else:
                    messages.error(request, 'Your account has been disabled.')
            else:
                # More detailed error for debugging
                logger.warning(f'Authentication failed for email: {email}')
                messages.error(request, 'Invalid email or password. Please try again.')
                
        except Exception as e:
            logger.error(f'Login error: {str(e)}')
            messages.error(request, f'Login failed: {str(e)}')
    
    return redirect('authentication:auth_page')

@never_cache
def logout_user(request):
    """Handle user logout"""
    email = request.user.email if request.user.is_authenticated else 'Unknown'
    try:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        logger.info(f'User logged out: {email}')
    except Exception as e:
        logger.error(f'Logout error: {str(e)}')
        messages.error(request, 'Logout failed.')
    
    return redirect('authentication:auth_page')

# AJAX validation functions
def check_email_availability(request):
    """Check if email is available"""
    email = request.GET.get('email', '').strip().lower()
    
    if not email:
        return JsonResponse({'available': False, 'message': 'Email required'})
    
    exists = CustomUser.objects.filter(email__iexact=email).exists()
    return JsonResponse({
        'available': not exists,
        'message': 'Email already registered' if exists else 'Email available'
    })

@login_required
def change_password_view(request):
    """Handle password change"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profil:profile')
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
    
    return redirect('profil:profile')

def terms_view(request):
    """Display terms and conditions"""
    return render(request, 'authentication/terms.html')

def login_view(request):
    """Display the login page"""
    # if request.user.is_authenticated:
    #     messages.info(request, f'You are already logged in as {request.user.email}.')
    #     return redirect('home')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')
            
    return render(request, 'authentication/login.html')

def signup_view(request):
    """Display the signup page"""
    # if request.user.is_authenticated:
    #     messages.info(request, f'You are already logged in as {request.user.email}.')
    #     return redirect('home')
        
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Log the user in
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password1')
                user = authenticate(email=email, password=password)
                login(request, user)
                return redirect('home')
            except ValueError as e:
                if 'already exists' in str(e):
                    messages.error(request, "A user with this email already exists.")
                    return render(request, 'authentication/signup.html', {'form': form})
                else:
                    raise
    else:
        form = CustomUserCreationForm()
    return render(request, 'authentication/signup.html', {'form': form})

def debug_auth(request):
    """Debug authentication issues"""
    debug_info = {
        'user_authenticated': request.user.is_authenticated,
        'user_email': request.user.email if request.user.is_authenticated else None,  # Changed from username to email
        'user_count': CustomUser.objects.count(),
        'active_users': CustomUser.objects.filter(is_active=True).count(),
        'session_key': request.session.session_key,
        'csrf_token': request.META.get('CSRF_COOKIE'),
        'remote_addr': request.META.get('REMOTE_ADDR'),
        'http_host': request.META.get('HTTP_HOST'),
        'user_agent': request.META.get('HTTP_USER_AGENT', '')[:100],
        'method': request.method,
        'is_authenticated': request.user.is_authenticated,
        'session_keys': list(request.session.keys()),
        'cookies': {k: v for k, v in request.COOKIES.items()},
        'post_data': {k: v for k, v in request.POST.items()} if request.method == 'POST' else {},
    }
    
    return JsonResponse(debug_info, json_dumps_params={'indent': 2})

@login_required
def delete_account(request):
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation', '')
        if confirmation == 'delete my account':
            try:
                user = request.user
                
                # Clean up history first (using the new history app)
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM history_history WHERE user_id = %s", [user.id])
                
                # Log user out
                from django.contrib.auth import logout
                logout(request)
                
                # Delete user directly with SQL to bypass foreign key checks
                with connection.cursor() as cursor:
                    cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
                    cursor.execute("DELETE FROM authentication_customuser WHERE id = %s", [user.id])
                    cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
                
                from django.contrib import messages
                messages.success(request, 'Your account has been deleted successfully.')
                return redirect('home')
                
            except Exception as e:
                from django.contrib import messages
                messages.error(request, f'Error deleting account: {str(e)}')
                return redirect('home')
        else:
            from django.contrib import messages
            messages.error(request, 'Please type "delete my account" to confirm deletion.')
    
    return render(request, 'authentication/delete_account.html')

def test_email(request):
    """Test email sending and configuration"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)
    
    # Show current email configuration
    config = {
        "EMAIL_BACKEND": settings.EMAIL_BACKEND,
        "EMAIL_HOST": settings.EMAIL_HOST,
        "EMAIL_PORT": settings.EMAIL_PORT,
        "EMAIL_USE_TLS": settings.EMAIL_USE_TLS,
        "EMAIL_HOST_USER": settings.EMAIL_HOST_USER,
        "DEFAULT_FROM_EMAIL": settings.DEFAULT_FROM_EMAIL,
        "USE_SMTP_IN_DEV": os.environ.get('USE_SMTP_IN_DEV', 'False'),
        "PASSWORD_SET": bool(settings.EMAIL_HOST_PASSWORD),
    }
    
    try:
        send_mail(
            'Test Email from AMRx Hub',
            'This is a test email to verify the email configuration is working.',
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False,
        )
        return JsonResponse({"status": "success", "message": "Email sent successfully", "config": config})
    except Exception as e:
        return JsonResponse({
            "status": "error", 
            "message": str(e),
            "config": config
        })

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            User = get_user_model()
            users = User.objects.filter(email__iexact=email.strip())

            if users.exists():
                user = users.first()
                subject = "Password Reset Requested"
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                protocol = "https" if request.is_secure() else "http"
                domain = request.get_host()

                try:
                    message = render_to_string("registration/password_reset_email.html", {
                        "protocol": protocol,
                        "domain": domain,
                        "uid": uid,
                        "uidb64": uid,
                        "token": token,
                        "user": user,
                    })
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    logger.exception(
                        "Password reset email failed for %s: %s",
                        user.email,
                        str(e),
                    )

            messages.success(
                request,
                "If an account with that email exists, a reset link has been sent."
            )
            return redirect("authentication:password_reset_done")
    else:
        form = PasswordResetForm()
    return render(request, "registration/password_reset_form.html", {"form": form})

def password_reset_done(request):
    return render(request, "registration/password_reset_done.html")

def password_reset_confirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may log in now.")
                return redirect("authentication:login")
        else:
            form = SetPasswordForm(user)
        return render(request, "registration/password_reset_confirm.html", {"form": form, "validlink": True})
    else:
        messages.error(request, "The reset link is invalid or has expired.")
        return render(request, "registration/password_reset_confirm.html", {"validlink": False})

def password_reset_complete(request):
    return render(request, "authentication/password_reset_complete.html")