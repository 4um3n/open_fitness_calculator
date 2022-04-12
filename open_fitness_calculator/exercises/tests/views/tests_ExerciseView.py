from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.exercises.models import Exercise
from open_fitness_calculator.profiles.models import Profile


class ExerciseViewTests(TestCase):
    __USER__MODEL = get_user_model()
    __EXERCISE_MODEL = Exercise
    __VALID_TEMPLATE_NAME = "exercises/user_exercise.html"
    __VALID_URL = None
    __VALID_ADMIN_FOOD_URL = None
    __VALID_REDIRECT_URL = reverse("list user exercises")

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

        url_kwargs = {"exercise_pk": self.exercise.pk}
        admin_url_kwargs = {"exercise_pk": self.admin_exercise.pk}
        self.__VALID_URL = reverse("exercise", kwargs=url_kwargs)
        self.__VALID_ADMIN_FOOD_URL = reverse("exercise", kwargs=admin_url_kwargs)

    def test_get__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.__USER__MODEL.objects.all().delete()

    def test_get__expect_correct_context(self):
        response = self.client.get(self.__VALID_URL)
        context = response.context_data

        self.assertEqual(self.exercise, context.get("exercise"))
        self.__USER__MODEL.objects.all().delete()

    def test_post__when_user_have_no_permissions__expect_ValidationError(self):
        response = self.client.post(self.__VALID_URL)
        expected_errors = "You have no permissions to do that!"

        self.assertFormError(response, form="form", field="__all__", errors=expected_errors)
        self.__USER__MODEL.objects.all().delete()

    def test_post__when_user_is_staff__expect_to_redirect(self):
        Profile.objects.filter(pk=self.user.pk).update(is_staff=True)
        request_data = {"name": self.exercise.name, "is_admin": True, "profile": ""}
        response = self.client.post(self.__VALID_URL, data=request_data)

        self.assertRedirects(response, self.__VALID_REDIRECT_URL)
        self.__USER__MODEL.objects.all().delete()

    def test_post__when_exercise_name_already_exists__expect_ValidationError(self):
        Profile.objects.filter(pk=self.user.pk).update(is_staff=True)
        request_data = {"name": self.admin_exercise.name, "is_admin": True, "profile": ""}
        response = self.client.post(self.__VALID_ADMIN_FOOD_URL, data=request_data)
        expected_errors = "Exercise with this name already exist!"

        self.assertFormError(response, form="form", field="__all__", errors=expected_errors)
        self.__USER__MODEL.objects.all().delete()
