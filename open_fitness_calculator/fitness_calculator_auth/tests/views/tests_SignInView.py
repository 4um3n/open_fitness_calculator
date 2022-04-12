from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class SignInViewTests(TestCase):
    __USER__MODEL = get_user_model()
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
        self.__USER__MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS).save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)
        response = self.client.get(self.__VALID_URL)
        self.assertRedirects(response, self.__VALID_REDIRECT_URL)
        self.__USER__MODEL.objects.all().delete()

    def test_post__when_username_provided__expect_success_and_redirect(self):
        user = self.__USER__MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        user.save()
        login_credentials = {
            "username": self.__VALID_USER_CREDENTIALS.get("username"),
            "password": self.__VALID_USER_CREDENTIALS.get("password"),
        }
        response = self.client.post(self.__VALID_URL, login_credentials)

        self.assertRedirects(response, self.__VALID_REDIRECT_URL)
        self.assertTrue(user.is_authenticated)
        self.__USER__MODEL.objects.all().delete()

    def test_post__when_email_provided__expect_success_and_redirect(self):
        user = self.__USER__MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        user.save()
        login_credentials = {
            "username": self.__VALID_USER_CREDENTIALS.get("email"),
            "password": self.__VALID_USER_CREDENTIALS.get("password"),
        }
        response = self.client.post(self.__VALID_URL, login_credentials)

        self.assertRedirects(response, self.__VALID_REDIRECT_URL)
        self.assertTrue(user.is_authenticated)
        self.__USER__MODEL.objects.all().delete()
