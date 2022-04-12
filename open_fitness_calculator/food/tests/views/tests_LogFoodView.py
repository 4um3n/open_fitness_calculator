from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.food.forms import FoodQuantityForm
from open_fitness_calculator.food.models import DiaryFood, Food


class LogFoodViewTests(TestCase):
    __USER_MODEL = get_user_model()
    __FOOD_MODEL = Food
    __VALID_TEMPLATE_NAME = "food/food.html"
    __VALID_FORM_CLASS = FoodQuantityForm
    __VALID_URL = None
    __VALID_REDIRECT_URL = reverse("profile diary")

    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }

    def setUp(self) -> None:
        self.user = self.__USER_MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        self.user.save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)
        self.food = self.__FOOD_MODEL.objects.create(name="Test", profile=self.user.profile)
        self.food.save()
        url_kwargs = {
            "food_pk": self.food.pk,
            "diary_pk": self.user.profile.diary_set.get(is_completed=False).pk,
            "meal": "Breakfast",
        }
        self.__VALID_URL = reverse("log food", kwargs=url_kwargs)

    def test_get__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.__USER_MODEL.objects.all().delete()

    def test_get__expect_correct_context(self):
        response = self.client.get(self.__VALID_URL)
        context = response.context_data
        p, c, f = self.food.get_percents_form_macros()

        self.assertTrue(isinstance(context.get("form"), self.__VALID_FORM_CLASS))
        self.assertEqual(self.food, context.get("food"))
        self.assertEqual("Breakfast", context.get("meal"))
        self.assertEqual(round(p, 2), context.get("protein_percents"))
        self.assertEqual(round(c, 2), context.get("carbs_percents"))
        self.assertEqual(round(f, 2), context.get("fat_percents"))
        self.__USER_MODEL.objects.all().delete()

    def test_post__when_objects_exists__expect_success(self):
        self.client.post(self.__VALID_URL, data={"quantity": 100})
        self.assertTrue(DiaryFood.objects.filter(food=self.food).exists())
        self.__USER_MODEL.objects.all().delete()

    def test_post__when_objects_dont_exists__expect_404_correct_template_used(self):
        url = reverse("log food", kwargs={"food_pk": 0, "diary_pk": 0, "meal": "Breakfast"})
        response = self.client.post(url, data={"quantity": 100})
        self.assertTemplateUsed(response, "404.html")
        self.__USER_MODEL.objects.all().delete()

    def test_post__when_objects_exists__expect_to_redirect(self):
        response = self.client.post(self.__VALID_URL, data={"quantity": 100})
        self.assertRedirects(response, self.__VALID_REDIRECT_URL)
        self.__USER_MODEL.objects.all().delete()
