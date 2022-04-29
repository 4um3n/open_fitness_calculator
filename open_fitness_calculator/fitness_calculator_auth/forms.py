from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from django.contrib.auth.password_validation import validate_password
from open_fitness_calculator.core.validators import validate_password_contain_digits, \
    validate_password_contain_uppercase_letter, validate_password_contain_lowercase_letter, validate_username_isalnum

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from open_fitness_calculator.core.forms import FormFieldsController, FitnessCalculatorModelForm
from open_fitness_calculator.fitness_calculator_auth.models import FitnessCalculatorUser


class SignUpForm(UserCreationForm, FormFieldsController):
    remove_labels = "__all__"
    class_name = "form-control auth"
    placeholders = {
        "username": "Username",
        "email": "Email",
        "password1": "Password",
        "password2": "Confirm password",
    }
    more_validators = {
        "username": [
            validate_username_isalnum,
        ],
        "password2": [
            validate_password,
            validate_password_contain_digits,
            validate_password_contain_uppercase_letter,
            validate_password_contain_lowercase_letter,
        ],
    }
    widgets_attrs = {
        "username": {
            "onfocus":
                "googleLikePlaceholderHandler('', 'id_username', 'id_username_legend')",
            "onblur":
                "googleLikePlaceholderHandler('Username', 'id_username', 'id_username_legend')",
        },
        "email": {
            "onfocus":
                "googleLikePlaceholderHandler('', 'id_email', 'id_email_legend')",
            "onblur":
                "googleLikePlaceholderHandler('Email', 'id_email', 'id_email_legend')",
        },
        "password1": {
            "onfocus":
                "googleLikePlaceholderHandler('', 'id_password1', 'id_password1_legend')",
            "onblur":
                "googleLikePlaceholderHandler('Password', 'id_password1', 'id_password1_legend')",
        },
        "password2": {
            "onfocus":
                "googleLikePlaceholderHandler('', 'id_password2', 'id_password2_legend')",
            "onblur":
                "googleLikePlaceholderHandler('Confirm Password', 'id_password2', 'id_password2_legend')",
        },
    }

    class Meta:
        model = FitnessCalculatorUser
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        super(SignUpForm, self).set_up_fields()


class SignInForm(AuthenticationForm, FormFieldsController):
    authenticated_user = None
    class_name = "form-control auth"
    placeholders = {
        "username": "Email address or username",
        "password": "Password",
    }
    widgets_attrs = {
        "username": {
            "onfocus":
                "googleLikePlaceholderHandler('', 'id_username', 'id_username_legend')",
            "onblur":
                "googleLikePlaceholderHandler('Email address or username', 'id_username', 'id_username_legend')",
        },
        "password": {
            "onfocus":
                "googleLikePlaceholderHandler('', 'id_password', 'id_password_legend')",
            "onblur":
                "googleLikePlaceholderHandler('Password', 'id_password', 'id_password_legend')",
        },
    }

    def __init__(self, *args, **kwargs):
        super(SignInForm, self).__init__(*args, **kwargs)
        super(SignInForm, self).set_up_fields()

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.authenticated_user = self.user_cache
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def save(self):
        return self.authenticated_user


class RequirePasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "autofocus": True,
                "placeholder": "Password",
                "class": "form-control user"
            },
        ),
    )

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(RequirePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        username = self.request.user.username
        password = self.cleaned_data.get('password')

        if password:
            user_cache = authenticate(self.request, username=username, password=password)
            if user_cache is None:
                raise ValidationError("Invalid Password!")

        return self.cleaned_data


class UpdateUserCredentialsForm(FitnessCalculatorModelForm):
    class_name = "form-control user"
    placeholders = {
        "username": "Username",
        "email": "Email",
    }

    class Meta:
        model = FitnessCalculatorUser
        fields = ["username", "email"]


class UpdateUserPasswordForm(SetPasswordForm, FormFieldsController):
    class_name = "form-control user"
    placeholders = {
        "new_password1": "New Password",
        "new_password2": "Confirm New Password",
    }
    widgets_attrs = {
        "new_password1": {"autofocus": True}
    }

    def __init__(self, *args, **kwargs):
        super(UpdateUserPasswordForm, self).__init__(*args, **kwargs)
        super(UpdateUserPasswordForm, self).set_up_fields()
