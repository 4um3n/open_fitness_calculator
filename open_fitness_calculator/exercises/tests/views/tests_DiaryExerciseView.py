from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.exercises.forms import ExerciseQuantityForm
from open_fitness_calculator.exercises.models import Exercise, DiaryExercise


class DiaryExerciseViewTests(TestCase):
    __USER_MODEL = get_user_model()
    __EXERCISE_MODEL = Exercise
    __DIARY_EXERCISE_MODEL = DiaryExercise
    __VALID_TEMPLATE_NAME = "exercises/diary_exercise.html"
    __VALID_FORM_CLASS = ExerciseQuantityForm
    __VALID_URL = None
    __VALID_REDIRECT_URL = None

    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }
    __VALID_EXERCISE_DATA = {
        "name": "Test",
        "unit": "set",
        "burned_calories_per_unit": 100,
    }

    def setUp(self) -> None:
        self.user = self.__USER_MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        self.user.save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)

        self.diary = self.user.profile.diary_set.get(is_completed=False)
        self.exercise = self.__EXERCISE_MODEL.objects.create(**self.__VALID_EXERCISE_DATA, profile=self.user.profile)
        self.exercise.save()
        self.diary_exercise = self.__DIARY_EXERCISE_MODEL.objects.create(
            diary=self.diary,
            exercise=self.exercise,
            quantity=100,
        )
        self.diary_exercise.save()

        url_kwargs = {
            "diary_pk": self.diary.pk,
            "exercise_pk": self.diary_exercise.pk,
        }
        self.__VALID_URL = reverse("diary exercise", kwargs=url_kwargs)
        self.__VALID_REDIRECT_URL = self.__VALID_URL

    def test_get__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.__USER_MODEL.objects.all().delete()

    def test_get__expect_correct_context(self):
        response = self.client.get(self.__VALID_URL)
        context = response.context_data
        expected_burned_calories = self.diary_exercise.exercise.burned_calories_per_unit * self.diary_exercise.quantity

        self.assertEqual(self.diary_exercise, context.get("diary_exercise"))
        self.assertEqual(expected_burned_calories, context.get("burned_calories"))
        self.assertEqual(self.diary.pk, context.get("diary_pk"))
        self.__USER_MODEL.objects.all().delete()
