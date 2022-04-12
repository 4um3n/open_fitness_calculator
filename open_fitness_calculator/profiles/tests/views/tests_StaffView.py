from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.profiles.forms import StaffForm
from open_fitness_calculator.profiles.models import Profile


class StaffViewTests(TestCase):
    __USER_MODEL = get_user_model()
    __VALID_TEMPLATE_NAME = "profile/profile_staff.html"
    __VALID_GET_REQUEST_URL = reverse("staff", kwargs={"profile_pk": 0})
    __VALID_POST_REQUEST_URL = None
    __VALID_FORM_CLASS = StaffForm
    __VALID_ADMIN_USER_CREDENTIALS = {
        "username": "admin ",
        "email": "admin@gmail.com",
        "password": "Passw0rd3",
    }
    __VALID_REGULAR_USER_CREDENTIALS = {
        "username": "regular",
        "email": "regular@gmail.com",
        "password": "Passw0rd3",
    }

    def setUp(self) -> None:
        self.admin_user = self.__USER_MODEL.objects.create_user(**self.__VALID_ADMIN_USER_CREDENTIALS)
        self.admin_user.save()
        self.client.login(**self.__VALID_ADMIN_USER_CREDENTIALS)

        self.regular_user = self.__USER_MODEL.objects.create_user(**self.__VALID_REGULAR_USER_CREDENTIALS)
        self.regular_user.save()
        
        self.__VALID_POST_REQUEST_URL = reverse("staff", kwargs={"profile_pk": self.regular_user.pk})

    def test_get__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_GET_REQUEST_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)

        self.__USER_MODEL.objects.all().delete()

    def test_get__expect_both_requested_staff_and_staff_to_be_empty(self):
        response = self.client.get(self.__VALID_GET_REQUEST_URL)

        self.assertEqual([], response.context_data.get("profiles_staff"))
        self.assertEqual([], response.context_data.get("profiles_requested_staff"))

        self.__USER_MODEL.objects.all().delete()

    def tests_get__expect_requested_staff_to_not_be_empty(self):
        Profile.objects.filter(pk=self.regular_user.profile.pk).update(requested_staff=True)
        response = self.client.get(self.__VALID_GET_REQUEST_URL)
        profiles_requested_staff = response.context_data.get("profiles_requested_staff")

        self.assertEqual([], response.context_data.get("profiles_staff"))
        self.assertEqual(1, len(profiles_requested_staff))
        self.assertEqual(2, len(profiles_requested_staff[0]))
        self.assertEqual(self.regular_user.profile, profiles_requested_staff[0][0])
        self.assertTrue(isinstance(profiles_requested_staff[0][1], self.__VALID_FORM_CLASS))

        self.__USER_MODEL.objects.all().delete()

    def test_post__when_requested_staff_is_not_empty__expect_success(self):
        Profile.objects.filter(pk=self.regular_user.profile.pk).update(requested_staff=True)
        self.client.post(self.__VALID_POST_REQUEST_URL)
        self.regular_user.profile.refresh_from_db()

        self.assertTrue(self.regular_user.profile.is_staff)

        self.__USER_MODEL.objects.all().delete()

    def test_post__when_staff_is_not_empty__expect_success(self):
        Profile.objects.filter(pk=self.regular_user.profile.pk).update(is_staff=True, requested_staff=True)
        self.client.post(self.__VALID_POST_REQUEST_URL)
        self.regular_user.profile.refresh_from_db()

        self.assertFalse(self.regular_user.profile.is_staff)
        self.assertTrue(self.regular_user.profile.requested_staff)

        self.__USER_MODEL.objects.all().delete()
