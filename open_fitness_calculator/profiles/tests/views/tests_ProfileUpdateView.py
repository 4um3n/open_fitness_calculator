from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.profiles.forms import ProfileForm, GoalForm


class ProfileUpdateViewTests(TestCase):
    __USER_MODEL = get_user_model()
    __VALID_TEMPLATE_NAME = "profile/profile_update.html"
    __VALID_URL = reverse("profile details")
    __VALID_REDIRECT_URL = reverse("password required")

    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }

    __VALID_POST_REQUEST_DATA = {
            "first_name": "Test",
            "last_name": "Test",
            "age": 21,
            "weight": 80,
            "height": 185,
            "gender": "female",
            "goal": "gain",
            "activity_level": "high",
            "per_week": 750,
        }

    __VALID_PROFILE_FORM_CLASS = ProfileForm
    __VALID_GOALS_FORM_CLASS = GoalForm

    def setUp(self) -> None:
        self.user = self.__USER_MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        self.user.save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)

    def test_get__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.__USER_MODEL.objects.all().delete()

    def test_get__expect_correct_context(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTrue(isinstance(response.context_data.get("form"), self.__VALID_PROFILE_FORM_CLASS))
        self.assertTrue(isinstance(response.context_data.get("goals_form"), self.__VALID_GOALS_FORM_CLASS))
        self.__USER_MODEL.objects.all().delete()

    def test_post__when_successful__expect_both_profile_and_profile_goals_changed(self):
        profile = self.user.profile

        self.assertEqual(profile.first_name, "")
        self.assertEqual(profile.last_name, "")
        self.assertEqual(profile.age, 14)
        self.assertEqual(profile.weight, 50)
        self.assertEqual(profile.height, 165)
        self.assertEqual(profile.gender, "male")
        self.assertEqual(profile.goal.goal, "maintain")
        self.assertEqual(profile.goal.activity_level, "medium")
        self.assertEqual(profile.goal.per_week, 500)

        self.client.post(self.__VALID_URL, data=self.__VALID_POST_REQUEST_DATA)
        profile.refresh_from_db()

        self.assertEqual(profile.first_name, self.__VALID_POST_REQUEST_DATA.get("first_name"))
        self.assertEqual(profile.last_name,  self.__VALID_POST_REQUEST_DATA.get("last_name"))
        self.assertEqual(profile.age,  self.__VALID_POST_REQUEST_DATA.get("age"))
        self.assertEqual(profile.weight,  self.__VALID_POST_REQUEST_DATA.get("weight"))
        self.assertEqual(profile.height,  self.__VALID_POST_REQUEST_DATA.get("height"))
        self.assertEqual(profile.gender,  self.__VALID_POST_REQUEST_DATA.get("gender"))
        self.assertEqual(profile.goal.goal,  self.__VALID_POST_REQUEST_DATA.get("goal"))
        self.assertEqual(profile.goal.activity_level,  self.__VALID_POST_REQUEST_DATA.get("activity_level"))
        self.assertEqual(profile.goal.per_week,  self.__VALID_POST_REQUEST_DATA.get("per_week"))

        self.__USER_MODEL.objects.all().delete()
