from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.food.models import DiaryFood, Food


class EnergyViewTests(TestCase):
    __USER__MODEL = get_user_model()
    __FOOD_MODEL = Food
    __DIARY_FOOD_MODEL = DiaryFood
    __VALID_TEMPLATE_NAME = "diary/energy.html"
    __VALID_URL = reverse("profile energy")
    __VALID_REDIRECT_URL = reverse("profile energy")
    __VALID_DELETE_DIARY_REDIRECT_URL = reverse("profile energy")

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
        total_cals, b_cals, l_cals, d_cals, s_cals = diary.meals_calories
        b_percents, l_percents, d_percents, s_percents = diary.get_meals_calories_percents()

        self.assertEqual(total_cals - diary.exercises_calories, context.get("eaten_cals"))
        self.assertEqual(diary.calories, context.get("goal_cals"))
        self.assertEqual(diary.remaining_calories, context.get("remaining_cals"))
        self.assertEqual(b_cals, context.get("breakfast_cals"))
        self.assertEqual(l_cals, context.get("lunch_cals"))
        self.assertEqual(d_cals, context.get("dinner_cals"))
        self.assertEqual(s_cals, context.get("snacks_cals"))
        self.assertEqual(b_percents, context.get("breakfast_percents"))
        self.assertEqual(l_percents, context.get("lunch_percents"))
        self.assertEqual(d_percents, context.get("dinner_percents"))
        self.assertEqual(s_percents, context.get("snacks_percents"))
        self.__USER__MODEL.objects.all().delete()

    def test_get__expect_correct_delete_diary_redirect_url(self):
        self.client.get(self.__VALID_URL)
        provided_url = self.client.session.get("delete_diary_redirect_url")

        self.assertEqual(self.__VALID_DELETE_DIARY_REDIRECT_URL, reverse(provided_url))
        self.__USER__MODEL.objects.all().delete()
