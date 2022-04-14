from django.db import models
from cloudinary import uploader
from cloudinary import models as cloudinary_models
from open_fitness_calculator.core.validators import validate_username_isalnum

from django.core.validators import MinValueValidator, MaxValueValidator
from open_fitness_calculator.core.mixins import DailyCaloriesCalculatorMixin
from open_fitness_calculator.fitness_calculator_auth.models import FitnessCalculatorUser


class Profile(models.Model):
    CHOICE_GENDER_MALE = "male"
    CHOICE_GENDER_FEMALE = "female"
    GENDER_CHOICES = (
        (CHOICE_GENDER_MALE, "Male"),
        (CHOICE_GENDER_FEMALE, "Female"),
    )

    is_admin = models.BooleanField(
        default=False,
    )
    is_staff = models.BooleanField(
        default=False,
    )
    requested_staff = models.BooleanField(
        default=False,
    )

    first_name = models.CharField(
        max_length=30,
        blank=True,
        validators=[
            validate_username_isalnum,
        ],
    )
    last_name = models.CharField(
        max_length=30,
        blank=True,
        validators=[
            validate_username_isalnum,
        ],
    )
    age = models.IntegerField(
        default=14,
        validators=[
            MinValueValidator(14),
            MaxValueValidator(150),
        ],
    )
    weight = models.FloatField(
        default=50,
        validators=[
            MinValueValidator(30),
            MaxValueValidator(500),
        ],
    )
    height = models.FloatField(
        default=165,
        validators=[
            MinValueValidator(100),
            MaxValueValidator(250),
        ],
    )
    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        blank=False,
        default="male",
    )

    user = models.OneToOneField(
        FitnessCalculatorUser,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    profile_picture = cloudinary_models.CloudinaryField(
        "Image",
        overwrite=True,
        resource_type="image",
        transformation={"quality": "auto:eco"},
        format="png",
        blank=True,
    )

    @property
    def cloudinary_dir_path(self):
        return f"images/profile_pictures/"

    def upload_new_profile_picture(self, new_image):
        return uploader.upload_resource(
            new_image,
            use_filename=True,
            unique_filename=False,
            filename_override=self.user.username,
            folder=self.cloudinary_dir_path,
        )

    def delete_profile_picture(self):
        uploader.destroy(f"{self.cloudinary_dir_path}{self.user.username}")

    def request_becoming_staff(self):
        self.requested_staff = True
        self.save()

    def __str__(self):
        return f"{self.user}"


class MacrosPercents(models.Model):
    class Meta:
        verbose_name_plural = "Macros Percents"

    profile = models.OneToOneField(
        to=Profile,
        on_delete=models.CASCADE,
        primary_key=True
    )

    protein = models.PositiveIntegerField(
        default=20,
        validators=[MaxValueValidator(100)],
    )
    carbs = models.PositiveIntegerField(
        default=50,
        validators=[MaxValueValidator(100)],
    )
    fat = models.PositiveIntegerField(
        default=30,
        validators=[MaxValueValidator(100)],
    )

    @property
    def percents(self) -> tuple:
        return self.protein / 100, self.carbs / 100, self.fat / 100

    def __str__(self):
        return f"{self.profile}"


class Goal(models.Model):
    CHOICE_LOOSE_WEIGHT = "loose"
    CHOICE_MAINTAIN_WEIGHT = "maintain"
    CHOICE_GAIN_WEIGHT = "gain"
    GOAL_CHOICES = (
        (CHOICE_LOOSE_WEIGHT, "Loose"),
        (CHOICE_MAINTAIN_WEIGHT, "Maintain"),
        (CHOICE_GAIN_WEIGHT, "Gain"),
    )

    CHOICE_NOT_ACTIVE = "not_active"
    CHOICE_LOW_ACTIVITY_LEVEL = "low"
    CHOICE_MEDIUM_ACTIVITY_LEVEL = "medium"
    CHOICE_HIGH_ACTIVITY_LEVEL = "high"
    ACTIVITY_LEVEL_CHOICES = (
        (CHOICE_NOT_ACTIVE, "Low"),
        (CHOICE_LOW_ACTIVITY_LEVEL, "Light"),
        (CHOICE_MEDIUM_ACTIVITY_LEVEL, "Medium"),
        (CHOICE_HIGH_ACTIVITY_LEVEL, "High"),
    )

    CHOICE_150_PER_WEEK = 150
    CHOICE_250_PER_WEEK = 250
    CHOICE_500_PER_WEEK = 500
    CHOICE_750_PER_WEEK = 750
    CHOICE_1000_PER_WEEK = 1000
    PER_WEEK_CHOICES = (
        (CHOICE_150_PER_WEEK, "150g"),
        (CHOICE_250_PER_WEEK, "250g"),
        (CHOICE_500_PER_WEEK, "500g"),
        (CHOICE_750_PER_WEEK, "750g"),
        (CHOICE_1000_PER_WEEK, "1000g"),
    )

    profile = models.OneToOneField(
        to=Profile,
        on_delete=models.CASCADE,
        primary_key=True
    )

    goal = models.CharField(
        max_length=10,
        choices=GOAL_CHOICES,
        blank=False,
        default="maintain",
    )

    activity_level = models.CharField(
        max_length=10,
        choices=ACTIVITY_LEVEL_CHOICES,
        blank=False,
        default="medium",
    )

    per_week = models.PositiveIntegerField(
        choices=PER_WEEK_CHOICES,
        blank=False,
        default=500,
    )

    def __str__(self):
        return f"{self.profile}"


class DailyNutrients(models.Model, DailyCaloriesCalculatorMixin):
    profile = models.OneToOneField(
        to=Profile,
        on_delete=models.CASCADE,
        primary_key=True
    )
    daily_calories = models.FloatField(default=0)
    daily_protein = models.FloatField(default=0)
    daily_carbs = models.FloatField(default=0)
    daily_fiber = models.FloatField(default=0)
    daily_sugars = models.FloatField(default=0)
    daily_fat = models.FloatField(default=0)
    daily_saturated_fat = models.FloatField(default=0)
    daily_monounsaturated_fat = models.FloatField(default=0)
    daily_polyunsaturated_fat = models.FloatField(default=0)
    daily_trans_fat = models.FloatField(default=0)
    daily_cholesterol = models.FloatField(default=300)
    daily_sodium = models.FloatField(default=2300)
    daily_potassium = models.FloatField(default=3500)
    daily_vitamin_a = models.FloatField(default=100)
    daily_vitamin_c = models.FloatField(default=100)
    daily_calcium = models.FloatField(default=100)
    daily_iron = models.FloatField(default=100)

    class Meta:
        verbose_name_plural = "Daily nutrients"

    def set_daily_nutrients(self) -> None:
        self.__set_calories()
        self.__set_nutrients()

    def __set_calories(self):
        self.daily_calories = self._calculate_daily_calories()

    def __set_nutrients(self):
        (self.daily_protein,
         self.daily_carbs,
         self.daily_sugars,
         self.daily_fiber,
         self.daily_fat,
         self.daily_saturated_fat,
         ) = self._calculate_daily_nutrients()

    def __str__(self):
        return f"{self.profile}"
