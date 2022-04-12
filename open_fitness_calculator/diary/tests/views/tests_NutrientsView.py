from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.food.models import DiaryFood, Food


class NutrientsViewTests(TestCase):
    __USER__MODEL = get_user_model()
    __FOOD_MODEL = Food
    __DIARY_FOOD_MODEL = DiaryFood
    __VALID_TEMPLATE_NAME = "diary/nutrients.html"
    __VALID_URL = reverse("profile nutrients")
    __VALID_REDIRECT_URL = reverse("profile nutrients")
    __VALID_DELETE_DIARY_REDIRECT_URL = reverse("profile nutrients")

    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }

    def setUp(self) -> None:
        self.user = self.__USER__MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        self.user.save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)

    def test_get__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.__USER__MODEL.objects.all().delete()

    def test_get__expect_correct_context(self):
        diary = self.user.profile.diary_set.get(is_completed=False)
        food = self.__FOOD_MODEL.objects.create(name="Test", profile=self.user.profile)
        food.save()

        self.__DIARY_FOOD_MODEL.objects.create(
            meal_type="Breakfast",
            diary=diary,
            food=food,
        ).save()

        response = self.client.get(self.__VALID_URL)
        context = response.context_data

        goal_nutrients = diary.macros
        eaten_nutrients = diary.eaten_macros
        remaining_nutrients = diary.remaining_macros
        goal_nutrients.update(diary.micros)
        eaten_nutrients.update(diary.eaten_micros)
        remaining_nutrients.update(diary.remaining_micros)

        expected_nutrients = {
            nutrient_name: (eaten_nutrients[nutrient_name], goal_nutrient, remaining_nutrients[nutrient_name])
            for nutrient_name, goal_nutrient in goal_nutrients.items()
        }
        expected_milligram_fields = ("cholesterol", "sodium", "potassium")
        expected_percents_fields = ("vitamin a", "vitamin c", "calcium", "iron")

        self.assertDictEqual(expected_nutrients, context.get("nutrients"))
        self.assertTupleEqual(expected_milligram_fields, context.get("mg_fields"))
        self.assertTupleEqual(expected_percents_fields, context.get("percents_fields"))
        self.__USER__MODEL.objects.all().delete()

    def test_get__expect_correct_delete_diary_redirect_url(self):
        self.client.get(self.__VALID_URL)
        provided_url = self.client.session.get("delete_diary_redirect_url")

        self.assertEqual(self.__VALID_DELETE_DIARY_REDIRECT_URL, reverse(provided_url))
        self.__USER__MODEL.objects.all().delete()
