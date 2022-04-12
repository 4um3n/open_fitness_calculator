from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class SignUpViewTests(TestCase):
    __USER__MODEL = get_user_model()
    __VALID_TEMPLATE_NAME = "fitness_calculator_auth/sign_up.html"
    __VALID_URL = reverse("sign up")
    __VALID_REDIRECT_URL_HOME = reverse("home")
    __VALID_REDIRECT_URL_PROFILE = reverse("profile details")
    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }

    def test_get__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)

    def test_get__when_user_logged_in__expect_to_redirect(self):
        user = self.__USER__MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        user.save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)
        response = self.client.get(self.__VALID_URL)
        self.assertRedirects(response, self.__VALID_REDIRECT_URL_HOME)
        self.__USER__MODEL.objects.all().delete()

    def test_post__when_successful__expect_to_redirect(self):
        username, email, password = self.__VALID_USER_CREDENTIALS.values()
        request_data = {
            "username": username,
            "email": email,
            "password1": password,
            "password2": password,
        }
        response = self.client.post(self.__VALID_URL, data=request_data)

        self.assertRedirects(response, self.__VALID_REDIRECT_URL_PROFILE)
        self.__USER__MODEL.objects.all().delete()
