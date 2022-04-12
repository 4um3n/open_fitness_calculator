from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.diary.forms import DiaryForm
from open_fitness_calculator.diary.models import Diary
from open_fitness_calculator.food.models import DiaryFood, Food


class DiaryViewTests(TestCase):
    __USER__MODEL = get_user_model()
    __DIARY_MODEL = Diary
    __FOOD_MODEL = Food
    __DIARY_FOOD_MODEL = DiaryFood
    __VALID_FORM_CLASS = DiaryForm
    __VALID_TEMPLATE_NAME = "diary/diary.html"
    __VALID_URL = reverse("profile diary")
    __VALID_REDIRECT_URL = reverse("profile diary")
    __VALID_DELETE_DIARY_REDIRECT_URL = reverse("profile diary")

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
        meals = diary.diaryfood_set.all()
        expected_meals_mapper = {
            "Breakfast": [meal for meal in meals if meal.meal_type == "Breakfast"],
            "Lunch": [meal for meal in meals if meal.meal_type == "Lunch"],
            "Dinner": [meal for meal in meals if meal.meal_type == "Dinner"],
            "Snack": [meal for meal in meals if meal.meal_type == "Snack"],
        }

        self.assertTrue(isinstance(context.get("form"), self.__VALID_FORM_CLASS))
        self.assertQuerysetEqual(context.get("exercises"), diary.diaryexercise_set.all())
        self.assertEqual(context.get("meals_mapper"), expected_meals_mapper)
        self.__USER__MODEL.objects.all().delete()

    def test_get__expect_correct_delete_diary_redirect_url(self):
        self.client.get(self.__VALID_URL)
        provided_url = self.client.session.get("delete_diary_redirect_url")

        self.assertEqual(self.__VALID_DELETE_DIARY_REDIRECT_URL, reverse(provided_url))
        self.__USER__MODEL.objects.all().delete()

    def test_get__when_page_not_provided__expect_correct_page(self):
        self.__DIARY_MODEL.objects.filter(profile=self.user.profile, is_completed=False).update(is_completed=True)
        self.__DIARY_MODEL.objects.create(profile=self.user.profile).save()
        response = self.client.get(self.__VALID_URL)

        self.assertEqual(2, response.context_data.get("page_obj").number)
        self.__USER__MODEL.objects.all().delete()

    def test_get__when_page_provided__expect_correct_page(self):
        self.__DIARY_MODEL.objects.filter(profile=self.user.profile, is_completed=False).update(is_completed=True)
        self.__DIARY_MODEL.objects.create(profile=self.user.profile).save()
        tmp_url = f"{self.__VALID_URL}?page=1"
        response = self.client.get(tmp_url)

        self.assertEqual(1, response.context_data.get("page_obj").number)
        self.__USER__MODEL.objects.all().delete()

    def test_get__when_page_cached__expect_correct_page(self):
        self.__DIARY_MODEL.objects.filter(profile=self.user.profile, is_completed=False).update(is_completed=True)
        self.__DIARY_MODEL.objects.create(profile=self.user.profile).save()
        tmp_url = f"{self.__VALID_URL}?page=1"
        self.client.get(tmp_url)
        response = self.client.get(self.__VALID_URL)

        self.assertEqual(1, response.context_data.get("page_obj").number)
        self.__USER__MODEL.objects.all().delete()

    def test_post__expect_success(self):
        diary = self.user.profile.diary_set.get(is_completed=False)
        response = self.client.get(self.__VALID_URL)
        data = response.context_data.get("form").initial
        self.client.post(self.__VALID_URL, data=data)
        diary.refresh_from_db()

        self.assertTrue(diary.is_completed)
        self.__USER__MODEL.objects.all().delete()

    def test_post__expect_to_redirect(self):
        get_response = self.client.get(self.__VALID_URL)
        data = get_response.context_data.get("form").initial
        post_response = self.client.post(self.__VALID_URL, data=data)

        self.assertRedirects(post_response, self.__VALID_REDIRECT_URL)
        self.__USER__MODEL.objects.all().delete()

    def test_post__expect_new_diary_created(self):
        self.assertEqual(1, len(self.user.profile.diary_set.all()))

        get_response = self.client.get(self.__VALID_URL)
        data = get_response.context_data.get("form").initial
        self.client.post(self.__VALID_URL, data=data)

        self.assertEqual(2, len(self.user.profile.diary_set.all()))
        self.__USER__MODEL.objects.all().delete()
