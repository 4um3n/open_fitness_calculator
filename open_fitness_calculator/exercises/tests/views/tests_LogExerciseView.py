from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.exercises.forms import ExerciseQuantityForm
from open_fitness_calculator.exercises.models import Exercise, DiaryExercise


class LogExerciseViewTests(TestCase):
    __USER_MODEL = get_user_model()
    __EXERCISE_MODEL = Exercise
    __VALID_TEMPLATE_NAME = "exercises/log_exercise.html"
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

        self.exercise = self.__EXERCISE_MODEL.objects.create(**self.__VALID_EXERCISE_DATA, profile=self.user.profile)
        self.exercise.save()

        url_kwargs = {
            "exercise_pk": self.exercise.pk,
            "diary_pk": self.user.profile.diary_set.get(is_completed=False).pk,
        }
        self.__VALID_URL = reverse("log exercise", kwargs=url_kwargs)

    def test_get__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.__USER_MODEL.objects.all().delete()

    def test_get__expect_correct_context(self):
        response = self.client.get(self.__VALID_URL)
        context = response.context_data

        self.assertTrue(isinstance(context.get("form"), self.__VALID_FORM_CLASS))
        self.assertEqual(self.exercise, context.get("exercise"))
        self.__USER_MODEL.objects.all().delete()

    def test_post__when_exercise_exists__expect_success(self):
        self.client.post(self.__VALID_URL, data={"quantity": 100})
        self.assertTrue(DiaryExercise.objects.filter(exercise=self.exercise).exists())
        self.__USER_MODEL.objects.all().delete()

    def test_post__when_exercise_does_not_exists__expect_404_correct_template_used(self):
        url = reverse("log exercise", kwargs={"exercise_pk": 0, "diary_pk": 0, })
        response = self.client.post(url, data={"quantity": 100})
        self.assertTemplateUsed(response, "404.html")
        self.__USER_MODEL.objects.all().delete()

    def test_post__when_exercise_exists__expect_to_redirect(self):
        response = self.client.post(self.__VALID_URL, data={"quantity": 100})
        self.assertRedirects(response, self.__VALID_REDIRECT_URL)
        self.__USER_MODEL.objects.all().delete()
