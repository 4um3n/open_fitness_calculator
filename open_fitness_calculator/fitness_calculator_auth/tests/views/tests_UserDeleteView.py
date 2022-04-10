from django.test import TestCase
from django.urls import reverse

from open_fitness_calculator.fitness_calculator_auth.models import FitnessCalculatorUser
from open_fitness_calculator.profiles.forms import ProfileForm, GoalForm


class UserDeleteViewTests(TestCase):
    __MODEL = FitnessCalculatorUser
    __VALID_TEMPLATE_NAME = "profile/profile_delete.html"
    __VALID_URL = reverse("user delete")
    __VALID_REDIRECT_URL = reverse("sign in")
    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }
    __VALID_PROFILE_FORM_CLASS = ProfileForm
    __VALID_GOALS_FORM_CLASS = GoalForm

    def setUp(self) -> None:
        self.user = FitnessCalculatorUser.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        self.user.save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)

    def test_get__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.user.delete()

    def test_get__expect_correct_context(self):
        response = self.client.get(self.__VALID_URL)
        self.assertEqual(self.user.profile, response.context_data.get("profile"))
        self.assertTrue(isinstance(response.context_data.get("form"), self.__VALID_PROFILE_FORM_CLASS))
        self.assertTrue(isinstance(response.context_data.get("goals_form"), self.__VALID_GOALS_FORM_CLASS))
        self.user.delete()

    def test_post__expect_user_deleted__expect_to_redirect(self):
        response = self.client.post(self.__VALID_URL)
        user_exists = self.__MODEL.objects.filter(pk=self.user.pk).exists()

        self.assertFalse(user_exists)
        self.assertRedirects(response, self.__VALID_REDIRECT_URL)
