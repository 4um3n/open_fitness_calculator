from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from open_fitness_calculator.food.models import Food
from open_fitness_calculator.profiles.models import Profile


class FoodViewTests(TestCase):
    __MODEL = get_user_model()
    __FOOD_MODEL = Food
    __VALID_TEMPLATE_NAME = "food/user_food.html"
    __VALID_URL = None
    __VALID_ADMIN_FOOD_URL = None
    __VALID_REDIRECT_URL = reverse("list user food")

    __VALID_USER_CREDENTIALS = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "Passw0rd3",
    }

    def setUp(self) -> None:
        self.user = self.__MODEL.objects.create_user(**self.__VALID_USER_CREDENTIALS)
        self.user.save()
        self.client.login(**self.__VALID_USER_CREDENTIALS)

        self.diary = self.user.profile.diary_set.get(is_completed=False)
        self.admin_food = self.__FOOD_MODEL.objects.create(name="TestAdmin", is_admin=True)
        self.admin_food.save()
        self.food = self.__FOOD_MODEL.objects.create(name="JustTest", profile=self.user.profile)
        self.food.save()

        url_kwargs = {"food_pk": self.food.pk}
        admin_url_kwargs = {"food_pk": self.admin_food.pk}
        self.__VALID_URL = reverse("food", kwargs=url_kwargs)
        self.__VALID_ADMIN_FOOD_URL = reverse("food", kwargs=admin_url_kwargs)

    def test_get__expect_correct_template_used(self):
        response = self.client.get(self.__VALID_URL)
        self.assertTemplateUsed(response, self.__VALID_TEMPLATE_NAME)
        self.__MODEL.objects.all().delete()
        Food.objects.all().delete()

    def test_get__expect_correct_context(self):
        response = self.client.get(self.__VALID_URL)
        context = response.context_data
        p, c, f = self.food.get_percents_form_macros()

        self.assertEqual(self.food, context.get("food"))
        self.assertEqual(round(p, 2), context.get("protein_percents"))
        self.assertEqual(round(c, 2), context.get("carbs_percents"))
        self.assertEqual(round(f, 2), context.get("fat_percents"))
        self.__MODEL.objects.all().delete()
        self.__FOOD_MODEL.objects.all().delete()

    def test_post__when_user_have_no_permissions__expect_ValidationError(self):
        response = self.client.post(self.__VALID_URL)
        expected_errors = "You have no permissions to do that!"

        self.assertFormError(response, form="form", field="__all__", errors=expected_errors)
        self.__MODEL.objects.all().delete()
        self.__FOOD_MODEL.objects.all().delete()

    def test_post__when_user_is_staff__expect_to_redirect(self):
        Profile.objects.filter(pk=self.user.pk).update(is_staff=True)
        request_data = {"name": self.food.name, "is_admin": True, "profile": ""}
        response = self.client.post(self.__VALID_URL, data=request_data)

        self.assertRedirects(response, self.__VALID_REDIRECT_URL)
        self.__MODEL.objects.all().delete()
        self.__FOOD_MODEL.objects.all().delete()
        
    def test_post__when_food_name_already_exists__expect_ValidationError(self):
        Profile.objects.filter(pk=self.user.pk).update(is_staff=True)
        request_data = {"name": self.admin_food.name, "is_admin": True, "profile": ""}
        response = self.client.post(self.__VALID_ADMIN_FOOD_URL, data=request_data)
        expected_errors = "Food with this name already exist!"

        self.assertFormError(response, form="form", field="__all__", errors=expected_errors)
        self.__MODEL.objects.all().delete()
        self.__FOOD_MODEL.objects.all().delete()
