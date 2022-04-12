from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class DiaryDeleteViewTests(TestCase):
    __USER__MODEL = get_user_model()
    __VALID_URL = reverse("profile delete diary", kwargs={"diary_pk": 1})
    __VALID_REDIRECT_URL = reverse("profile diary")

    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }

    def setUp(self) -> None:
        self.user = self.__USER__MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        self.user.save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)

    def test_get__when_deleting_not_completed_diary__expect_diary_deleted_and_new_one_crated(self):
        diary = self.user.profile.diary_set.get(is_completed=False)

        self.assertEqual(1, len(self.user.profile.diary_set.all()))
        self.assertTrue(self.user.profile.diary_set.filter(pk=diary.pk).exists())
        self.assertTrue(self.user.profile.diary_set.filter(is_completed=False).exists())

        self.client.get(self.__VALID_URL)

        self.assertEqual(1, len(self.user.profile.diary_set.all()))
        self.assertFalse(self.user.profile.diary_set.filter(pk=diary.pk).exists())
        self.assertTrue(self.user.profile.diary_set.filter(is_completed=False).exists())
        self.__USER__MODEL.objects.all().delete()

    def test_get__when_delete_diary_redirect_url_provided__expect_correct_redirect(self):
        session = self.client.session
        session["delete_diary_redirect_url"] = "profile energy"
        session.save()
        response = self.client.get(self.__VALID_URL)

        self.assertRedirects(response, reverse("profile energy"))
        self.__USER__MODEL.objects.all().delete()

    def test_get__when_delete_diary_redirect_url_not_provided__expect_correct_redirect(self):
        response = self.client.get(self.__VALID_URL)

        self.assertRedirects(response, self.__VALID_REDIRECT_URL)
        self.__USER__MODEL.objects.all().delete()
