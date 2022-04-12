from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from open_fitness_calculator.core.forms import FitnessCalculatorModelForm
from open_fitness_calculator.core.validators import validate_username_isalnum
from open_fitness_calculator.profiles.models import Profile, Goal, MacrosPercents


class ProfileForm(FitnessCalculatorModelForm):
    remove_labels = "__all__"
    class_name = "form-control profile"
    classes_excluded = [
        "user",
        "gender",
        "profile_picture",
        "is_admin",
        "is_staff",
    ]
    more_classes = {
        "profile_picture": "form-control-profile-picture",
        "gender": "form-control-radio gender",
    }
    placeholders = {
        "first_name": "First name",
        "last_name": "Last name",
        "age": "Age",
        "weight": "Weight",
        "height": "Height",
    }
    more_validators = {
        "first_name": [validate_username_isalnum],
        "last_name": [validate_username_isalnum],
        "age": [MinValueValidator(14), MaxValueValidator(150), ],
        "weight": [MinValueValidator(1), MaxValueValidator(500), ],
        "height": [MinValueValidator(100), MaxValueValidator(250), ],
    }
    widgets_attrs = {
        "profile_picture": {
            "onchange": "profilePictureChanged()",
            "hidden": "hidden",
        },
    }

    class Meta:
        model = Profile
        exclude = ["user", "is_admin", "is_staff", "requested_staff"]
        widgets = {
            "gender": forms.RadioSelect(),
            "profile_picture": forms.FileInput(),
        }


class StaffForm(FitnessCalculatorModelForm):
    class_name = "is-staff-checkbox"
    widgets_attrs = {
        "is_staff": {
            "hidden": "hidden",
        },
    }

    class Meta:
        model = Profile
        fields = ["is_staff"]
        widgets = {
            "is_staff": forms.CheckboxInput(),
        }


class GoalForm(FitnessCalculatorModelForm):
    more_classes = {
        "goal": "form-control-radio goal",
        "activity_level": "form-control-radio active-level",
        "per_week": "form-control-radio per-week",
    }

    class Meta:
        model = Goal
        exclude = ["profile"]
        widgets = {
            "goal": forms.RadioSelect(),
            "per_week": forms.RadioSelect(),
            "activity_level": forms.RadioSelect(),
        }


class MacrosPercentsForm(FitnessCalculatorModelForm):
    class_name = "form-control-macros"

    class Meta:
        model = MacrosPercents
        exclude = ["profile"]

    def clean(self):
        if sum(self.cleaned_data.values()) != 100:
            self.add_error("__all__", "The sum of the percents must be equal to 100")

        return super(MacrosPercentsForm, self).clean()
