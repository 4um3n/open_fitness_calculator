from django import forms
from django.core.validators import MinValueValidator
from open_fitness_calculator.core.forms import FitnessCalculatorModelForm, BaseSearchForm
from open_fitness_calculator.core.mixins import FoodMacrosConvertorMixin
from open_fitness_calculator.food.models import Food, DiaryFood


class FoodQuantityForm(forms.ModelForm):
    class Meta:
        model = DiaryFood
        fields = ["quantity"]
        widgets = {
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control food-quantity",
                    "placeholder": "100",
                },
            ),
        }


class SearchFoodForm(BaseSearchForm):
    accurate_search = forms.BooleanField(
        label="",
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "accurate-search-checkbox",
            },
        ),
    )


class FoodForm(FitnessCalculatorModelForm, FoodMacrosConvertorMixin):
    remove_labels = "__all__"
    validators = [MinValueValidator(0)]
    validators_excluded = [
        "name",
        "ingredients",
        "category",
    ]
    class_name = "form-control create-food"
    more_classes = {
        "name": "left",
        "ingredients": "left",
    }
    placeholders = {
        "name": "Name",
        "ingredients": "Ingredients",
        "category": "Category",
        "energy": "Energy kcal",
        "protein": "Protein g",
        "carbs": "Total carbohydrates g",
        "fiber": "Fibers g",
        "sugars": "Sugars g",
        "fat": "Total fat g",
        "saturated_fat": "Saturated fat g",
        "polyunsaturated_fat": "Polyunsaturated fat g",
        "monounsaturated_fat": "Monounsaturated fat g",
        "trans_fat": "Trans fat g",
        "cholesterol": "Cholesterol mg",
        "sodium": "Sodium mg",
        "calcium": "Calcium %",
        "iron": "Iron %",
        "potassium": "Potassium mg",
        "vitamin_a": "Vitamin A %",
        "vitamin_c": "Vitamin C %",
    }

    class Meta:
        model = Food
        exclude = [
            "profile",
            "pie_chart",
            "is_admin",
            "waiting_for_upload",
        ]

    def __init__(self, *args, is_open_food=False, profile=None, **kwargs):
        self.is_open_food = is_open_food
        self.profile = profile
        super(FoodForm, self).__init__(*args, **kwargs)

    def clean(self):
        provided_energy = self.cleaned_data.get("energy") or 0
        required_macros = (
            self.cleaned_data.get("protein") or 0,
            self.cleaned_data.get("carbs") or 0,
            self.cleaned_data.get("fat") or 0,
        )

        if any(required_macros) and provided_energy:
            energy = int(sum(self.get_calories_form_macros(*required_macros)))
            if energy != provided_energy and not self.is_open_food:
                self.add_error(
                    "energy",
                    f"You set the energy to {provided_energy}, but it seems to be {energy}"
                )

        return super(FoodForm, self).clean()


class AdminFoodForm(FitnessCalculatorModelForm):
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
        model = Food
        fields = ["is_admin", "profile", "name"]
