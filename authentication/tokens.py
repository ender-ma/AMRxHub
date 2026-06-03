from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    PasswordResetTokenGenerator with a separate timeout for email verification.
    """

    def check_token(self, user, token):
        if not (user and token):
            return False
        try:
            ts_b36, _hash = token.split("-")
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Constant-time comparison against expected token
        if not constant_time_compare(self._make_token_with_timestamp(user, ts), token):
            return False

        timeout = getattr(settings, "EMAIL_VERIFICATION_TIMEOUT", 60 * 60 * 24)
        return (self._num_seconds(self._now()) - ts) <= timeout

email_verification_token = EmailVerificationTokenGenerator()