from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.food.models import Food


class ListAvailableFoodViewTests(TestCase):
    __USER__MODEL = get_user_model()
    __FOOD_MODEL = Food
    __VALID_TEMPLATE_NAME = "food/list_available_food.html"
    __VALID_URL = None

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
        self.admin_food = self.__FOOD_MODEL.objects.create(name="TestAdmin", is_admin=True)
        self.admin_food.save()
        self.food = self.__FOOD_MODEL.objects.create(name="JustTest", profile=self.user.profile)
        self.food.save()

        url_kwargs = {
            "diary_pk": self.diary.pk,
            "meal": "Breakfast",
        }
        self.__VALID_URL = reverse("list available food", kwargs=url_kwargs)

    def test_get__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.__USER__MODEL.objects.all().delete()
        self.__FOOD_MODEL.objects.all().delete()

    def test_get__expect_correct_context(self):
        response = self.client.get(self.__VALID_URL)
        context = response.context_data

        self.assertEqual("Breakfast", context.get("meal_type"))
        self.assertEqual(self.diary.pk, context.get("diary_pk"))
        self.assertEqual(2, len(context.get("food")))
        self.assertEqual(self.food, context.get("food")[0])
        self.assertEqual(self.admin_food, context.get("food")[1])
        self.__USER__MODEL.objects.all().delete()
        self.__FOOD_MODEL.objects.all().delete()

    def test_post__expect_correct_food(self):
        tmp_food = self.__FOOD_MODEL.objects.create(name="Admin", profile=self.user.profile)
        tmp_food.save()
        response = self.client.post(self.__VALID_URL, data={"searched_string": "admin"})
        context = response.context_data

        self.assertEqual(3, len(Food.objects.all()))
        self.assertEqual(2, len(context.get("food")))
        self.assertEqual(tmp_food, context.get("food")[0])
        self.assertEqual(self.admin_food, context.get("food")[1])
        self.__USER__MODEL.objects.all().delete()
        self.__FOOD_MODEL.objects.all().delete()

