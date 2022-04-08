from django.core.exceptions import ValidationError


def validate_username_isalnum(value: str) -> None:
    if not value.isalnum():
        raise ValidationError(f"Username can contain only alphanumeric characters.")


def validate_password_contain_uppercase_letter(value: str) -> None:
    if not any([char.isupper() for char in value]):
        raise ValidationError("Password must contain at least one uppercase letter.")


def validate_password_contain_lowercase_letter(value: str) -> None:
    if not any([char.islower() for char in value]):
        raise ValidationError(f"Password must contain at least one lowercase letter.")


def validate_password_contain_digits(value: str) -> None:
    if not any([char.isdigit() for char in value]):
        raise ValidationError(f"Password must contain at least one digit.")
