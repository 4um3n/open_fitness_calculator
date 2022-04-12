from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.fitness_calculator_auth.forms import RequirePasswordForm


class RequirePasswordViewTests(TestCase):
    __USER__MODEL = get_user_model()
    __VALID_FORM_CLASS = RequirePasswordForm
    __VALID_TEMPLATE_NAME = "fitness_calculator_auth/require_password.html"
    __VALID_URL = reverse("password required")
    __VALID_REDIRECT_URL = reverse("home")
    __VALID_NEXT_URL = reverse("update user credentials")

    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }

    def setUp(self) -> None:
        self.user = self.__USER__MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        self.user.save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)

    def test_get__when_successful__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.__USER__MODEL.objects.all().delete()

    def test_get__when_successful__expect_correct_context(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTrue(isinstance(response.context_data.get("form"), self.__VALID_FORM_CLASS))
        self.__USER__MODEL.objects.all().delete()

    def test_post__when_next_url_provided__expect_to_redirect(self):
        url = f"{self.__VALID_URL}?next={self.__VALID_NEXT_URL}"
        request_data = {"password": self.__VALID_USER_CREDENTIALS.get("password")}
        response = self.client.post(url, data=request_data)
        self.assertRedirects(response, self.__VALID_NEXT_URL)
        self.__USER__MODEL.objects.all().delete()

    def test_post__when_next_url_not_provided__expect_to_redirect(self):
        request_data = {"password": self.__VALID_USER_CREDENTIALS.get("password")}
        response = self.client.post(self.__VALID_URL, data=request_data)
        self.assertRedirects(response, self.__VALID_REDIRECT_URL)
        self.__USER__MODEL.objects.all().delete()
