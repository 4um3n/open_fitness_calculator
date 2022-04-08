from django import forms

from open_fitness_calculator.core.forms import FitnessCalculatorModelForm
from open_fitness_calculator.exercises.models import Exercise, DiaryExercise


class ExerciseQuantityForm(forms.ModelForm):
    class Meta:
        model = DiaryExercise
        fields = ["quantity"]
        widgets = {
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control food-quantity exercise",
                    "placeholder": "1",
                },
            ),
        }


class SearchExerciseForm(forms.Form):
    searched_string = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "search-bar",
                "placeholder": "Search...",
            },
        ),
    )


class ExerciseForm(FitnessCalculatorModelForm):
    class_name = "form-control exercise"
    placeholders = {
        "name": "Name",
        "unit": "Unit",
        "burned_calories_per_unit": "Burned",
    }
    more_classes = {
        "name": "left",
        "burned_calories_per_unit": "burned-calories"
    }
    widgets_attrs = {
        "name": {
            "autofocus": "autofocus"
        },
    }

    class Meta:
        model = Exercise
        exclude = ["profile", "is_admin"]


class AdminExerciseForm(FitnessCalculatorModelForm):
    widgets_attrs = {
        "is_admin": {
            "hidden": "hidden",
        },
        "profile": {
            "hidden": "hidden",
        },
        "name": {
            "hidden": "hidden",
        },
    }

    class Meta:
        model = Exercise
        fields = ["is_admin", "profile", "name"]
