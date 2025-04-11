from django.core.exceptions import ValidationError
import re

class SpecialCharacterValidator:
    """
    Validate that the password contains at least one special character.
    """
    def validate(self, password, user=None):
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                "Password must contain at least one special character.",
                code='password_no_special_char',
            )

    def get_help_text(self):
        return "Your password must contain at least one special character."

class UpperLowerCaseValidator:
    """
    Validate that the password contains both uppercase and lowercase letters.
    """
    def validate(self, password, user=None):
        if not (any(char.isupper() for char in password) and any(char.islower() for char in password)):
            raise ValidationError(
                "Password must contain both uppercase and lowercase letters.",
                code='password_no_mixed_case',
            )

    def get_help_text(self):
        return "Your password must contain both uppercase and lowercase letters."