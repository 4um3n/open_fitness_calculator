from django.test import TestCase
from django.urls import reverse

from open_fitness_calculator.fitness_calculator_auth.forms import RequirePasswordForm
from open_fitness_calculator.fitness_calculator_auth.models import FitnessCalculatorUser


class RequirePasswordViewTests(TestCase):
    __MODEL = FitnessCalculatorUser
    __VALID_FORM_CLASS = RequirePasswordForm
    __VALID_TEMPLATE_NAME = "fitness_calculator_auth/require_password.html"
    __VALID_URL = reverse("password required")
    __VALID_REDIRECT_URL = reverse("home")
    __VALID_NEXT_URL = "fitness_calculator_auth/require_password.html"
    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }

    def setUp(self) -> None:
        self.user = self.__MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        self.user.save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)

    def test_get__when_successful__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.user.delete()

    def test_get__when_successful__expect_correct_context(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTrue(isinstance(response.context_data.get("form"), self.__VALID_FORM_CLASS))
        self.user.delete()

    def test_post__when_next_url_provided__expect_to_redirect(self):
        url = f"{self.__VALID_URL}?next={reverse('update user credentials')}"
        request_data = {"password": self.__VALID_USER_CREDENTIALS.get("password")}
        response = self.client.post(url, data=request_data)
        self.assertRedirects(response, reverse("update user credentials"))
        self.user.delete()

    def test_post__when_next_url_not_provided__expect_to_redirect(self):
        request_data = {"password": self.__VALID_USER_CREDENTIALS.get("password")}
        response = self.client.post(self.__VALID_URL, data=request_data)
        self.assertRedirects(response, self.__VALID_REDIRECT_URL)
        self.user.delete()
