import os
from pathlib import Path

import cloudinary

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

from urllib.parse import urlparse, parse_qsl

BASE_DIR = Path(__file__).resolve().parent.parent

# Explicitly load .env from the project root
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: list[str]) -> list[str]:
    raw = os.environ.get(name, "")
    if not raw.strip():
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


# -----------------------------------------------------------------------------
# Core
# -----------------------------------------------------------------------------
DEBUG = env_bool("DEBUG", False)
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development").strip().lower()

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key" if DEBUG else "")
if not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY environment variable is required when DEBUG=False")


# -----------------------------------------------------------------------------
# Hosts / CSRF
# -----------------------------------------------------------------------------
ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    [
        "localhost",
        "127.0.0.1",
        ".vscode-cdn.net",
        ".gitpod.io",
        ".codespaces.app",
        "amrxhub.com",
        "www.amrxhub.com",
        "amrxhub-production.up.railway.app",
        "www.amrxhub-production.up.railway.app",
    ],
)

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    [
        "https://*.vscode-cdn.net",
        "https://*.gitpod.io",
        "https://*.codespaces.app",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1",
        "https://amrxhub.com",
        "https://www.amrxhub.com",
        "https://amrxhub-production.up.railway.app",
        "https://www.amrxhub-production.up.railway.app",
    ],
)


# -----------------------------------------------------------------------------
# Apps / Middleware
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "main",
    "authentication",
    "tools",
    "profil",
    "notifications",
    "history",
    "resources",
#    "socials",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "channels",
    "anymail",
]

AUTH_USER_MODEL = "authentication.CustomUser"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

if not DEBUG:
    MIDDLEWARE.append("django.middleware.http.ConditionalGetMiddleware")

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


# -----------------------------------------------------------------------------
# URLs / WSGI / ASGI / Templates
# -----------------------------------------------------------------------------
ROOT_URLCONF = "main.urls"
WSGI_APPLICATION = "main.wsgi.application"
ASGI_APPLICATION = "main.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "authentication" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# -----------------------------------------------------------------------------
# Database (unified db URL parsing for both development and production using Neon PostgreSQL)
# -----------------------------------------------------------------------------
database_url = os.getenv("DATABASE_URL", "").strip().strip("'\"")
if not database_url:
    if DEBUG:
        # Build-time fallback so collectstatic can import settings
        database_url = "postgresql://placeholder:placeholder@localhost:5432/placeholder"
    else:
        raise ImproperlyConfigured("DATABASE_URL is required.")

DATABASES = {
    'default': dj_database_url.config(
        default=database_url,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# -----------------------------------------------------------------------------
# Cloudinary Configuration
# -----------------------------------------------------------------------------

if os.getenv("CLOUDINARY_URL"):
    cloudinary.config(secure=True)


# -----------------------------------------------------------------------------
# Password Validation
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 6},
    },
    {"NAME": "authentication.validators.CustomPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# -----------------------------------------------------------------------------
# Allauth
# -----------------------------------------------------------------------------
SITE_ID = int(os.environ.get("SITE_ID", "1"))

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_DISPLAY = lambda user: user.email
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http" if DEBUG else "https"

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "EMAIL_AUTHENTICATION": True,
        "EMAIL_AUTHENTICATION_AUTO_CONNECT": True,
    }
}

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    SOCIALACCOUNT_PROVIDERS["google"]["APP"] = {
        "client_id": GOOGLE_CLIENT_ID,
        "secret": GOOGLE_CLIENT_SECRET,
    }
elif DEBUG:
    # This helps you see why it's failing in your terminal
    import warnings
    warnings.warn("GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET missing from environment. Google login will fail.")

SOCIALACCOUNT_STORE_TOKENS = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True # False Get the user to confirm before signing up
SOCIALACCOUNT_ADAPTER = "authentication.adapters.CustomSocialAccountAdapter"


# -----------------------------------------------------------------------------
# I18N / TZ
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "en-ng"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static / Media
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

if os.getenv("CLOUDINARY_URL"):
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# -----------------------------------------------------------------------------
# Session / Security
# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/auth/"
LOGOUT_REDIRECT_URL = "/auth/"

PASSWORD_RESET_TIMEOUT = 1500
EMAIL_VERIFICATION_TIMEOUT = 60 * 60 * 24

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SAMESITE = "Lax"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_DOMAIN = os.environ.get("SESSION_COOKIE_DOMAIN", None)

CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# -----------------------------------------------------------------------------
# Email
# -----------------------------------------------------------------------------
USE_SMTP_IN_DEV = env_bool("USE_SMTP_IN_DEV", False)
BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "").strip()

if USE_SMTP_IN_DEV or ENVIRONMENT == "production":
    if not BREVO_API_KEY:
        raise ImproperlyConfigured("BREVO_API_KEY is required when using the Brevo email backend.")
    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

ANYMAIL = {
    "BREVO_API_KEY": os.environ.get("BREVO_API_KEY"),
}

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "")
EMAIL_TIMEOUT = int(os.environ.get("EMAIL_TIMEOUT", "5"))

# -----------------------------------------------------------------------------
# Channels / Celery / Cache
# -----------------------------------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "memory://")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "cache")
CELERY_CACHE_BACKEND = os.environ.get("CELERY_CACHE_BACKEND", "memory")
CELERY_TASK_ALWAYS_EAGER = env_bool("CELERY_TASK_ALWAYS_EAGER", True)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


# -----------------------------------------------------------------------------
# Site metadata
# -----------------------------------------------------------------------------
SITE_DOMAIN = os.environ.get("SITE_DOMAIN", "")
SITE_PROTOCOL = os.environ.get("SITE_PROTOCOL", "")


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.mail": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
