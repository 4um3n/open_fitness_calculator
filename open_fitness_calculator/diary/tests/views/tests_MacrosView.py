from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.food.models import DiaryFood, Food
from open_fitness_calculator.profiles.forms import MacrosPercentsForm


class MacrosViewTests(TestCase):
    __USER__MODEL = get_user_model()
    __FOOD_MODEL = Food
    __DIARY_FOOD_MODEL = DiaryFood
    __VALID_FORM_CLASS = MacrosPercentsForm
    __VALID_TEMPLATE_NAME = "diary/macros.html"
    __VALID_URL = reverse("profile macros")
    __VALID_REDIRECT_URL = reverse("profile macros")
    __VALID_DELETE_DIARY_REDIRECT_URL = reverse("profile macros")

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
        p_grams, c_grams, f_grams = diary.meals_base_macros
        eaten_p_percents, eaten_c_percents, eaten_f_percents = diary.get_meals_macros_percents()

        self.assertTrue(isinstance(context.get("form"), self.__VALID_FORM_CLASS))
        self.assertEqual(p_grams, context.get("protein_grams"))
        self.assertEqual(c_grams, context.get("carbs_grams"))
        self.assertEqual(f_grams, context.get("fat_grams"))
        self.assertEqual(eaten_p_percents, context.get("eaten_protein_percent"))
        self.assertEqual(eaten_c_percents, context.get("eaten_carbs_percents"))
        self.assertEqual(eaten_f_percents, context.get("eaten_fat_percents"))
        self.__USER__MODEL.objects.all().delete()

    def test_get__expect_correct_delete_diary_redirect_url(self):
        self.client.get(self.__VALID_URL)
        provided_url = self.client.session.get("delete_diary_redirect_url")

        self.assertEqual(self.__VALID_DELETE_DIARY_REDIRECT_URL, reverse(provided_url))
        self.__USER__MODEL.objects.all().delete()

    def test_post__when_data_is_valid__expect_success(self):
        macros_percents = self.user.profile.macrospercents

        self.assertEqual(20, macros_percents.protein)
        self.assertEqual(50, macros_percents.carbs)
        self.assertEqual(30, macros_percents.fat)

        data = {
            "protein": 35,
            "carbs": 40,
            "fat": 25,
        }
        self.client.post(self.__VALID_URL, data=data)
        macros_percents.refresh_from_db()

        self.assertEqual(35, macros_percents.protein)
        self.assertEqual(40, macros_percents.carbs)
        self.assertEqual(25, macros_percents.fat)
        self.__USER__MODEL.objects.all().delete()

    def test_post__when_data_is_invalid__expect_form_errors(self):
        macros_percents = self.user.profile.macrospercents

        self.assertEqual(20, macros_percents.protein)
        self.assertEqual(50, macros_percents.carbs)
        self.assertEqual(30, macros_percents.fat)

        data = {
            "protein": 40,
            "carbs": 40,
            "fat": 25,
        }
        response = self.client.post(self.__VALID_URL, data=data)
        expected_errors = "The sum of the percents must be equal to 100"

        self.assertFormError(response, form="form", field="__all__", errors=expected_errors)
        self.__USER__MODEL.objects.all().delete()

    def test_post__expect_to_redirect(self):
        get_response = self.client.get(self.__VALID_URL)
        data = get_response.context_data.get("form").initial
        post_response = self.client.post(self.__VALID_URL, data=data)

        self.assertRedirects(post_response, self.__VALID_REDIRECT_URL)
        self.__USER__MODEL.objects.all().delete()
