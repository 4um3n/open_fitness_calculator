from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.food.forms import FoodQuantityForm
from open_fitness_calculator.food.models import Food, DiaryFood


class DiaryFoodViewTests(TestCase):
    __USER_MODEL = get_user_model()
    __VALID_TEMPLATE_NAME = "food/diary_food.html"
    __VALID_FORM_CLASS = FoodQuantityForm
    __VALID_URL = None
    __VALID_REDIRECT_URL = None

    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }

    def setUp(self) -> None:
        self.user = self.__USER_MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        self.user.save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)

        self.diary = self.user.profile.diary_set.get(is_completed=False)
        self.food = Food.objects.create(name="Test", profile=self.user.profile)
        self.food.save()
        self.diary_food = DiaryFood.objects.create(
            meal_type="Breakfast",
            diary=self.diary,
            food=self.food,
            quantity=100,
        )
        self.diary_food.save()

        url_kwargs = {
            "diary_pk": self.diary.pk,
            "meal_pk": self.food.pk,
        }
        self.__VALID_URL = reverse("meal food", kwargs=url_kwargs)
        self.__VALID_REDIRECT_URL = self.__VALID_URL

    def test_get__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.__USER_MODEL.objects.all().delete()

    def test_get__expect_correct_context(self):
        response = self.client.get(self.__VALID_URL)
        expected_context = self.diary_food.get_nutrients_by_quantity()
        p, c, f = self.diary_food.food.get_percents_form_macros(
            expected_context.get("energy"),
            expected_context.get("protein"),
            expected_context.get("carbs"),
            expected_context.get("fat"),
        )
        expected_context.update(
            {
                "protein_percents": round(p, 2),
                "carbs_percents": round(c, 2),
                "fat_percents": round(f, 2),
                "meal": self.diary_food,
                "diary_pk": self.diary.pk,
            }
        )

        self.assertTrue(isinstance(response.context_data.get("form"), self.__VALID_FORM_CLASS))
        self.assertDictContainsSubset(expected_context, response.context_data)
        self.__USER_MODEL.objects.all().delete()
