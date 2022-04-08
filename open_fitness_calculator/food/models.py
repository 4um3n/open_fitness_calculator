from django.db import models
from django.core.validators import MinValueValidator

from open_fitness_calculator.core.mixins import FoodPieChartMixin, FoodMacrosConvertorMixin
from open_fitness_calculator.diary.models import Diary
from open_fitness_calculator.fitness_calculator_auth.models import FitnessCalculatorUser
from open_fitness_calculator.profiles.models import Profile


class FoodCategory(models.Model):
    name = models.CharField(
        max_length=25,
    )

    class Meta:
        verbose_name_plural = "Food Categories"

    def __str__(self):
        return f"{self.name}"


class Food(models.Model, FoodMacrosConvertorMixin):
    not_number_fields = [
        "id",
        "name",
        "ingredients",
        "category_id",
        "is_admin",
        "pie_chart",
        "profile_id",
        "_state",
    ]

    name = models.CharField(
        max_length=100,
    )
    ingredients = models.CharField(
        max_length=500,
        default="",
        blank=True,
    )
    category = models.ForeignKey(
        FoodCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    is_admin = models.BooleanField(
        default=False,
    )
    energy = models.IntegerField(
        default=0,
        null=True,
        blank=True,
    )
    protein = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )
    carbs = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )
    fiber = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )
    sugars = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )
    fat = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )
    saturated_fat = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )
    polyunsaturated_fat = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )
    monounsaturated_fat = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )
    trans_fat = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )
    cholesterol = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )
    sodium = models.FloatField(
        null=True,
        default=0,
        blank=True,
    )
    potassium = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )
    calcium = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )
    iron = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )
    vitamin_a = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )
    vitamin_c = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )
    profile = models.ForeignKey(
        to=Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = "Food"

    def __str__(self):
        return f"{self.name}"


class FoodPieChart(models.Model, FoodPieChartMixin):
    image = models.ImageField(
        default="images/food/default/default.png"
    )

    food = models.OneToOneField(
        to=Food,
        on_delete=models.CASCADE,
    )

    @property
    def name(self):
        return self.food.name

    def __str__(self):
        return f"{self.name}"


class DiaryFood(models.Model):
    CHOICE_BREAKFAST = "Breakfast"
    CHOICE_LUNCH = "Lunch"
    CHOICE_DINNER = "Dinner"
    CHOICE_SNACK = "Snack"
    MEAL_TYPE_CHOICES = (
        (CHOICE_BREAKFAST, "Breakfast"),
        (CHOICE_LUNCH, "Lunch"),
        (CHOICE_DINNER, "Dinner"),
        (CHOICE_SNACK, "Snack"),
    )

    meal_type = models.CharField(
        max_length=9,
        choices=MEAL_TYPE_CHOICES,
    )
    diary = models.ForeignKey(
        to=Diary,
        on_delete=models.CASCADE,
    )
    food = models.ForeignKey(
        to=Food,
        on_delete=models.CASCADE,
    )
    quantity = models.FloatField(
        default=100,
        validators=[
            MinValueValidator(0),
        ],
    )

    @property
    def quantity_percents(self):
        return self.quantity / 100

    def get_nutrients_by_quantity(self) -> dict:
        return {
            field: value * self.quantity_percents
            for field, value in self.food.__dict__.items()
            if field not in self.food.not_number_fields
        }

    def get_eaten_calories(self):
        return self.food.energy * self.quantity_percents

    def __str__(self):
        return f"{self.meal_type}:{self.food}:{self.diary}"
