import profile
import uuid
import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
import smtplib
import dns.resolver
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect

def email_verified_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("authentication:login")
        if not request.user.is_email_verified:
            messages.warning(
                request,
                "Please verify your email to access the Social and history page.",
                extra_tags="auto-dismiss-5s",
            )
            return redirect("profil:profile")
        return view_func(request, *args, **kwargs)
    return _wrapped


def generate_verification_token():
    """Generate a unique token for email verification"""
    return uuid.uuid4().hex


# def verify_smtp_credentials():
#     try:
#         server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
#         server.starttls()
#         server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
#         server.quit()
#         return True
#     except Exception as e:
#         logging.error(f"SMTP verification failed: {e}")
#         return False

def email_domain_has_mx(email):
    domain = email.split('@')[-1]
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except Exception:
        return False