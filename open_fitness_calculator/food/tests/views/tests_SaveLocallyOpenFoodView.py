from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.food.models import Food
from open_fitness_calculator.core.mixins import GetOpenFoodMixin, FoodMacrosConvertorMixin


class SaveLocallyOpenFoodViewTests(TestCase):
    __MODEL = get_user_model()
    __VALID_TEMPLATE_NAME = "food/save_open_food.html"
    __VALID_FOOD_PK = 279649
    __VALID_URL = reverse("save locally open food", kwargs={"food_pk": __VALID_FOOD_PK})

    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }

    def setUp(self) -> None:
        self.user = self.__MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        self.user.save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)
        self.get_open_food_service = GetOpenFoodMixin()
        self.food_macros_convertor_service = FoodMacrosConvertorMixin()
        
    def test_get__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.__MODEL.objects.all().delete()
    
    def test_get__expect_correct_context(self):
        expected_context = self.get_open_food_service.get_food_by_id(self.__VALID_FOOD_PK)
        response = self.client.get(self.__VALID_URL)
        context = response.context_data

        p_percents, c_percents, f_percents = self.food_macros_convertor_service.get_percents_form_macros(
            context.get("energy"),
            context.get("protein"),
            context.get("carbs"),
            context.get("fat"),
        )
        expected_context.update(
            {
                "protein_percents": p_percents,
                "carbs_percents": c_percents,
                "fat_percents": f_percents,
            }
        )

        self.assertDictContainsSubset(expected_context, context)
        self.__MODEL.objects.all().delete()

    def test_post__when_successful__expect_to_redirect(self):
        request_data = self.get_open_food_service.get_food_by_id(self.__VALID_FOOD_PK)
        request_data = {k: v or "" for k, v in request_data.items()}
        response = self.client.post(self.__VALID_URL, data=request_data)

        food = self.user.profile.food_set.reverse()[0]
        expected_redirect_url = reverse("food", kwargs={"food_pk": food.pk})

        self.assertRedirects(response, expected_redirect_url)
        self.__MODEL.objects.all().delete()
        Food.objects.all().delete()

    def test_post__when_food_name_exists_in_user_food__expect_ValidationError(self):
        Food.objects.create(name="kiwi", profile=self.user.profile)
        request_data = self.get_open_food_service.get_food_by_id(self.__VALID_FOOD_PK)
        request_data = {k: v or "" for k, v in request_data.items()}
        response = self.client.post(self.__VALID_URL, data=request_data)
        expected_errors = "Food with that name already exists"

        self.assertFormError(response, form="form", field="name", errors=expected_errors)
        self.__MODEL.objects.all().delete()
        Food.objects.all().delete()
