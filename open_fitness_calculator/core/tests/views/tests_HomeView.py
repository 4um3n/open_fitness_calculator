from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class HomeViwTests(TestCase):
    __USER__MODEL = get_user_model()
    __VALID_TEMPLATE_NAME = "core/home.html"
    __VALID_URL = reverse("home")
    __VALID_FOOD_LEN_PER_PAGE = 6
    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }
    __VALID_OPEN_FOOD_NAME = "kiwi"

    def setUp(self) -> None:
        self.user = self.__USER__MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        self.user.save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)
        self.diary = self.user.profile.diary_set.get(is_completed=False)

    def test_get__expect_correct_template_name(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.__USER__MODEL.objects.all().delete()

    def test_get__expect_correct_context(self):
        response = self.client.get(self.__VALID_URL)

        self.assertEqual(1, response.context.get("page_obj").number)
        self.assertEqual(0, len(response.context.get("food")))
        self.assertEqual(self.user, response.context.get("user"))
        self.assertEqual(int(self.diary.calories), response.context.get("calories"))
        self.assertEqual(int(self.diary.eaten_calories), response.context.get("eaten_calories"))
        self.assertEqual(int(self.diary.exercises_calories), response.context.get("exercises_calories"))
        self.assertEqual(int(self.diary.remaining_calories), response.context.get("remaining_calories"))
        self.__USER__MODEL.objects.all().delete()

    def test_post__when_accurate_search_off__expect_correct_context(self):
        request_data = {
            "searched_string": self.__VALID_OPEN_FOOD_NAME,
            "accurate_search": False
        }
        response = self.client.post(self.__VALID_URL, data=request_data)

        self.assertEqual(1, response.context.get("page_obj").number)
        self.assertEqual(self.__VALID_FOOD_LEN_PER_PAGE, len(response.context.get("food")))
        self.__USER__MODEL.objects.all().delete()

    def test_post__when_accurate_search_on__expect_correct_context(self):
        request_data = {
            "searched_string": self.__VALID_OPEN_FOOD_NAME,
            "accurate_search": True
        }
        response = self.client.post(self.__VALID_URL, data=request_data)

        self.assertEqual(1, response.context.get("page_obj").number)
        self.assertEqual(self.__VALID_FOOD_LEN_PER_PAGE, len(response.context.get("food")))
        self.__USER__MODEL.objects.all().delete()

    def test_get__when_post_was_successful__expect_correct_food_to_be_cached(self):
        request_data = {
            "searched_string": self.__VALID_OPEN_FOOD_NAME,
            "accurate_search": False
        }
        self.client.post(self.__VALID_URL, data=request_data)
        response = self.client.get(f"{self.__VALID_URL}?page=1")

        self.assertEqual(1, response.context.get("page_obj").number)
        self.assertEqual(self.__VALID_FOOD_LEN_PER_PAGE, len(response.context.get("food")))

        response = self.client.get(f"{self.__VALID_URL}?page=2")

        self.assertEqual(2, response.context.get("page_obj").number)
        self.assertEqual(self.__VALID_FOOD_LEN_PER_PAGE, len(response.context.get("food")))
        self.__USER__MODEL.objects.all().delete()
