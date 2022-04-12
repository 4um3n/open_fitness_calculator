from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.food.forms import FoodQuantityForm
from open_fitness_calculator.food.models import Food, DiaryFood


class DeleteFoodFromDiaryViewTests(TestCase):
    __USER__MODEL = get_user_model()
    __FOOD_MODEL = Food
    __DIARY_FOOD_MODEL = DiaryFood
    __VALID_FORM_CLASS = FoodQuantityForm
    __VALID_URL = None
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

        self.diary = self.user.profile.diary_set.get(is_completed=False)
        self.food = self.__FOOD_MODEL.objects.create(name="Test", profile=self.user.profile)
        self.food.save()
        self.diary_food = self.__DIARY_FOOD_MODEL.objects.create(
            meal_type="Breakfast",
            diary=self.diary,
            food=self.food,
            quantity=100,
        )
        self.diary_food.save()

        url_kwargs = {"meal_pk": self.diary_food.pk}
        self.__VALID_URL = reverse("delete food from diary", kwargs=url_kwargs)

    def test_get__when_successful__expect_to_redirect(self):
        response = self.client.get(self.__VALID_URL)
        self.assertRedirects(response, self.__VALID_REDIRECT_URL)
        self.__USER__MODEL.objects.all().delete()

    def test_get__when_meal_does_not_exist__expect_404_correct_template_used(self):
        url = reverse("delete food from diary", kwargs={"meal_pk": 0})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "404.html")
        self.__USER__MODEL.objects.all().delete()
        
        