from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.exercises.forms import ExerciseQuantityForm
from open_fitness_calculator.exercises.models import Exercise, DiaryExercise


class DeleteExerciseFromDiaryViewTests(TestCase):
    __USER_MODEL = get_user_model()
    __EXERCISE_MODEL = Exercise
    __DIARY_EXERCISE_MODEL = DiaryExercise
    __VALID_FORM_CLASS = ExerciseQuantityForm
    __VALID_URL = None
    __VALID_REDIRECT_URL = reverse("profile diary")

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

        url_kwargs = {"exercise_pk": self.diary_exercise.pk}
        self.__VALID_URL = reverse("delete exercise from diary", kwargs=url_kwargs)

    def test_get__when_successful__expect_to_redirect(self):
        response = self.client.get(self.__VALID_URL)
        self.assertRedirects(response, self.__VALID_REDIRECT_URL)
        self.__USER_MODEL.objects.all().delete()

    def test_get__when_meal_does_not_exist__expect_404_correct_template_used(self):
        url = reverse("delete exercise from diary", kwargs={"exercise_pk": 0})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "404.html")
        self.__USER_MODEL.objects.all().delete()

