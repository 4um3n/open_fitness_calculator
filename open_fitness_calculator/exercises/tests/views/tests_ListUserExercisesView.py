from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.exercises.models import Exercise


class ListUserExercisesViewTests(TestCase):
    __USER__MODEL = get_user_model()
    __EXERCISE_MODEL = Exercise
    __VALID_TEMPLATE_NAME = "exercises/list_user_exercises.html"
    __VALID_URL = reverse("list user exercises")

    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }
    __VALID_EXERCISE_DATA = {
        "unit": "set",
        "burned_calories_per_unit": 100,
    }

    def setUp(self) -> None:
        self.user = self.__USER__MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        self.user.save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)

        self.diary = self.user.profile.diary_set.get(is_completed=False)
        self.admin_exercise = self.__EXERCISE_MODEL.objects.create(
            **self.__VALID_EXERCISE_DATA,
            name="TestAdmin",
            is_admin=True
        )
        self.admin_exercise.save()
        self.exercise = self.__EXERCISE_MODEL.objects.create(
            **self.__VALID_EXERCISE_DATA,
            name="JustTest",
            profile=self.user.profile
        )
        self.exercise.save()

    def test_get__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.__USER__MODEL.objects.all().delete()

    def test_get__expect_correct_context(self):
        response = self.client.get(self.__VALID_URL)
        context = response.context_data

        self.assertEqual(2, len(context.get("exercises")))
        self.assertEqual(self.exercise, context.get("exercises")[0])
        self.assertEqual(self.admin_exercise, context.get("exercises")[1])
        self.__USER__MODEL.objects.all().delete()
        self.__EXERCISE_MODEL.objects.all().delete()

    def test_post__expect_correct_food(self):
        tmp_exercise = self.__EXERCISE_MODEL.objects.create(
            **self.__VALID_EXERCISE_DATA,
            name="Admin",
            profile=self.user.profile
        )
        tmp_exercise.save()
        response = self.client.post(self.__VALID_URL, data={"searched_string": "admin"})
        context = response.context_data

        self.assertEqual(3, len(self.__EXERCISE_MODEL.objects.all()))
        self.assertEqual(2, len(context.get("exercises")))
        self.assertEqual(tmp_exercise, context.get("exercises")[0])
        self.assertEqual(self.admin_exercise, context.get("exercises")[1])
        self.__USER__MODEL.objects.all().delete()
