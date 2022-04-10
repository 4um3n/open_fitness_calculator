from django.test import TestCase
from django.urls import reverse

from open_fitness_calculator.fitness_calculator_auth.models import FitnessCalculatorUser


class SignInViewTests(TestCase):
    __MODEL = FitnessCalculatorUser
    __VALID_TEMPLATE_NAME = "fitness_calculator_auth/sign_in.html"
    __VALID_URL = reverse("sign in")
    __VALID_REDIRECT_URL = reverse("home")
    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }

    def test_get__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)

    def test_get__when_user_logged_in__expect_to_redirect(self):
        self.__MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS).save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)
        response = self.client.get(self.__VALID_URL)
        self.assertRedirects(response, self.__VALID_REDIRECT_URL)
        self.__MODEL.objects.first().delete()
