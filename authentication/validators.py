from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
# Import the built-in validator to inherit from it
from django.contrib.auth.password_validation import MinimumLengthValidator

class CustomMinimumLengthValidator(MinimumLengthValidator):
    """
    Inherits from the default MinimumLengthValidator but overrides the help text.
    """
    def get_help_text(self):
        # Return an empty string to prevent help text from showing on the form.
        return ""
    
class CustomPasswordValidator:
    """
    Validates that the password contains at least one uppercase letter and one number.
    """
    def validate(self, password, user=None):
        if not any(char.isupper() for char in password):
            raise ValidationError(
                _("Your password must contain at least one uppercase letter."),
                code='password_no_upper',
            )
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                _("Your password must contain at least one number."),
                code='password_no_number',
            )

    def get_help_text(self):
        # This method is required by Django's form rendering.
        # Returning an empty string prevents any help text from being displayed.
        return ""