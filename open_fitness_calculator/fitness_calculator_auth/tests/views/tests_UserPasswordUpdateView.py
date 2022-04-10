from django.test import TestCase
from django.urls import reverse

from open_fitness_calculator.fitness_calculator_auth.models import FitnessCalculatorUser


class UserPasswordUpdateViewTests(TestCase):
    __MODEL = FitnessCalculatorUser
    __VALID_TEMPLATE_NAME = "fitness_calculator_auth/update_user_password.html"
    __VALID_URL = reverse("update user password")
    __VALID_REDIRECT_URL = reverse("password required")
    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }

    def setUp(self) -> None:
        self.user = FitnessCalculatorUser.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        self.user.save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)

    def test_get__expect_to_redirect(self):
        response = self.client.get(self.__VALID_URL)
        expected_redirect_url = f"{self.__VALID_REDIRECT_URL}?next={self.__VALID_URL}"

        self.assertRedirects(response, expected_redirect_url)
        self.user.delete()

    def test_get__expect_correct_template_used(self):
        request_data = {"password": self.__VALID_USER_CREDENTIALS.get("password")}
        url = f"{self.__VALID_REDIRECT_URL}?next={self.__VALID_URL}"
        self.client.post(url, data=request_data)
        response = self.client.get(self.__VALID_URL)

        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.user.delete()

    def test_get__expect_correct_context(self):
        request_data = {"password": self.__VALID_USER_CREDENTIALS.get("password")}
        url = f"{self.__VALID_REDIRECT_URL}?next={self.__VALID_URL}"
        self.client.post(url, data=request_data)
        response = self.client.get(self.__VALID_URL)

        self.assertEqual(self.user.profile, response.context_data.get("profile"))
        self.user.delete()
