import os

from django.db import models
from cloudinary import uploader
from cloudinary import models as cloudinary_models
from django.core.validators import MinValueValidator

from open_fitness_calculator.diary.models import Diary
from open_fitness_calculator.profiles.models import Profile
from open_fitness_calculator.core.mixins import BaseFoodPieChartMixin, FoodMacrosConvertorMixin
from open_fitness_calculator.fitness_calculator_auth.models import FitnessCalculatorUser


class FoodCategory(models.Model):
    RED_MEAT_CHOICE = "red_meat"
    WHITE_MEAT_CHOICE = "white_meat"
    FISH_CHOICE = "fish"
    ROOT_VEGETABLES_CHOICE = "root_vegetables"
    GREEN_LEAFY_VEGETABLES_CHOICE = "green_leafy_vegetables"
    FRUIT_CHOICE = "fruits"
    BERRIE_CHOICE = "berries"
    NAME_CHOICES = (
        (RED_MEAT_CHOICE, "Red Meat"),
        (WHITE_MEAT_CHOICE, "White Meat"),
        (FRUIT_CHOICE, "Fish"),
        (RED_MEAT_CHOICE, "Root Vegetables"),
        (GREEN_LEAFY_VEGETABLES_CHOICE, "Green Leafy Vegetables"),
        (FRUIT_CHOICE, "Fruits"),
        (BERRIE_CHOICE, "Berries"),
    )

    name = models.CharField(
        max_length=25,
        choices=NAME_CHOICES,
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
    is_admin = models.BooleanField(default=False)
    energy = models.IntegerField(default=0)
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fiber = models.FloatField(default=0)
    sugars = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    saturated_fat = models.FloatField(default=0)
    polyunsaturated_fat = models.FloatField(default=0)
    monounsaturated_fat = models.FloatField(default=0)
    trans_fat = models.FloatField(default=0)
    cholesterol = models.FloatField(default=0)
    sodium = models.FloatField(default=0)
    potassium = models.FloatField(default=0)
    calcium = models.FloatField(default=0)
    iron = models.FloatField(default=0)
    vitamin_a = models.FloatField(default=0)
    vitamin_c = models.FloatField(default=0)
    profile = models.ForeignKey(
        to=Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = "Food"

    def __str__(self):
        return f"{self.name}_{self.pk}"


class FoodPieChart(models.Model, BaseFoodPieChartMixin):
    food = models.OneToOneField(
        to=Food,
        on_delete=models.CASCADE,
    )

    image = cloudinary_models.CloudinaryField(
        "Image",
        overwrite=True,
        resource_type="image",
        transformation={"quality": "auto:eco"},
        format="png",
    )

    @property
    def name(self):
        return self.food.name

    @classmethod
    def __reset_image(cls, pk, new_image):
        cls.objects.filter(pk=pk).update(image=new_image)

    def reset_pie_chart(self):
        self.create_pie_chart()
        new_pie_chart = self._upload_new_pie_chart()
        self.__reset_image(self.pk, new_pie_chart)
        self._delete_unused_local_pie_chart()

    def delete_cloudinary_pie_chart(self):
        self._delete_unused_cloudinary_pie_chart()

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
