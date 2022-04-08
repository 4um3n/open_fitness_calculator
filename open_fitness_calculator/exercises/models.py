from django.core.validators import MaxValueValidator
from django.db import models
from open_fitness_calculator.diary.models import Diary
from open_fitness_calculator.profiles.models import Profile


class Exercise(models.Model):
    MINUTE_UNIT_CHOICE = "minute"
    HOUR_UNIT_CHOICE = "hour"
    SET_UNIT_CHOICE = "set"
    UNIT_CHOICES = (
        (MINUTE_UNIT_CHOICE, "minute"),
        (HOUR_UNIT_CHOICE, "hour"),
        (SET_UNIT_CHOICE, "set"),
    )

    name = models.CharField(
        max_length=100,
        unique=True,
    )
    unit = models.CharField(
        max_length=6,
        choices=UNIT_CHOICES,
    )
    is_admin = models.BooleanField(
        default=False,
    )
    burned_calories_per_unit = models.PositiveIntegerField()

    profile = models.ForeignKey(
        to=Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name}"


class DiaryExercise(models.Model):
    diary = models.ForeignKey(
        to=Diary,
        on_delete=models.CASCADE,
    )
    exercise = models.ForeignKey(
        to=Exercise,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[
            MaxValueValidator(1000000000),
        ],
    )

    def get_burned_calories(self):
        return self.quantity * self.exercise.burned_calories_per_unit

    def __str__(self):
        return f"{self.exercise}:{self.diary}"
