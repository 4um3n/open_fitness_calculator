from itertools import chain
from rest_framework import status
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.http import QueryDict
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from open_fitness_calculator.diary.models import Diary
from open_fitness_calculator.food.models import Food, DiaryFood
from open_fitness_calculator.food.serializers import FoodSerializer
from open_fitness_calculator.core.mixins import GetOpenFoodMixin, FoodMacrosConvertorMixin, FoodPreSaveValidatorMixin
from open_fitness_calculator.food.forms import FoodForm, SearchFoodForm, FoodQuantityForm, AdminFoodForm
from django.views.generic import CreateView, UpdateView, FormView, RedirectView, DetailView, DeleteView


@method_decorator(never_cache, name="dispatch")
@method_decorator(login_required, name="dispatch")
class BaseFoodView(DetailView):
    object = None
    model = Food
    pk_url_kwarg = "food_pk"

    def get_extra_context_data(self, **kwargs):
        food = kwargs.get("food") or self.get_object()
        protein_percents, carbs_percents, fat_percents = food.get_percents_form_macros()

        self.extra_context = {
            "food": food,
            "meal": self.kwargs.get("meal"),
            "protein_percents": round(protein_percents, 2),
            "carbs_percents": round(carbs_percents, 2),
            "fat_percents": round(fat_percents, 2),
        }

        return self.extra_context


class LogFoodView(BaseFoodView, FormView):
    form_class = FoodQuantityForm
    template_name = "food/log_food.html"
    success_url = reverse_lazy("profile diary")

    def get_context_data(self, **kwargs):
        self.get_extra_context_data()
        return super(LogFoodView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        diary = get_object_or_404(Diary, pk=self.kwargs.get("diary_pk"))
        DiaryFood.objects.create(
            diary=diary,
            meal_type=self.kwargs.get("meal"),
            food=self.get_object(),
            quantity=form.cleaned_data.get("quantity"),
        ).save()
        return super(LogFoodView, self).form_valid(form)


@method_decorator(never_cache, name="dispatch")
@method_decorator(login_required, name="dispatch")
class DiaryFoodView(UpdateView):
    model = DiaryFood
    form_class = FoodQuantityForm
    pk_url_kwarg = "meal_pk"
    template_name = "food/diary_food.html"

    def get_success_url(self):
        kwargs = {
            "diary_pk": self.kwargs.get("diary_pk"),
            "meal_pk": self.kwargs.get("meal_pk"),
        }
        return reverse_lazy("meal food", kwargs=kwargs)

    def get_context_data(self, **kwargs):
        meal = self.get_object()
        self.extra_context = meal.get_nutrients_by_quantity()
        energy = self.extra_context.get("energy")
        protein = self.extra_context.get("protein")
        carbs = self.extra_context.get("carbs")
        fat = self.extra_context.get("fat")

        protein_percents, carbs_percents, fat_percents = meal.food.get_percents_form_macros(
            energy, protein, carbs, fat
        )

        self.extra_context.update({
            "protein_percents": round(protein_percents, 2),
            "carbs_percents": round(carbs_percents, 2),
            "fat_percents": round(fat_percents, 2),
            "meal": meal,
            "diary_pk": self.kwargs.get("diary_pk"),
        })

        return super(DiaryFoodView, self).get_context_data(**kwargs)


@method_decorator(login_required, name="dispatch")
class DeleteFoodFromDiaryView(RedirectView):
    url = reverse_lazy("profile diary")

    def get(self, request, *args, **kwargs):
        meal = get_object_or_404(DiaryFood, pk=self.kwargs.get("meal_pk"))
        meal.delete()
        return super(DeleteFoodFromDiaryView, self).get(request, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class ListAvailableFoodView(FormView):
    form_class = SearchFoodForm
    template_name = "food/list_available_food.html"

    def get_food(self):
        food = Food.objects.filter(is_admin=True)
        user_food = Food.objects.filter(profile=self.request.user.profile)
        return list(sorted(chain(food, user_food), key=lambda f: f.name))

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(food=self.get_food()))

    def get_context_data(self, **kwargs):
        food = kwargs.get("food")
        self.extra_context = {
            "meal_type": self.kwargs.get("meal"),
            "diary_pk": self.kwargs.get("diary_pk"),
            "food": food if food is not None else self.get_food(),
        }
        return super(ListAvailableFoodView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        food = self.get_food()
        searched_str = form.cleaned_data.get("searched_string")
        searched_str = searched_str.lower() if searched_str else ""
        food = [f for f in food if f.name.lower() in searched_str or searched_str in f.name.lower()]
        return self.render_to_response(self.get_context_data(food=food))


@method_decorator(login_required, name="dispatch")
class ListUserFoodView(FormView):
    form_class = SearchFoodForm
    template_name = "food/list_user_food.html"

    def get_food(self):
        profile = self.request.user.profile
        user_food = Food.objects.filter(profile=profile)
        admin_food = Food.objects.filter(is_admin=True)
        return list(sorted(chain(user_food, admin_food), key=lambda f: f.name))

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(food=self.get_food()))

    def get_context_data(self, **kwargs):
        food = kwargs.get("food")
        self.extra_context = {"food": food if food is not None else self.get_food()}
        return super(ListUserFoodView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        user_food = self.get_food()
        searched_str = form.cleaned_data.get("searched_string")
        searched_str = searched_str.lower() if searched_str else ""
        food = [f for f in user_food if f.name.lower() in searched_str or searched_str in f.name.lower()]
        return self.render_to_response(self.get_context_data(food=food))


class FoodView(BaseFoodView, UpdateView, FoodPreSaveValidatorMixin):
    form_class = AdminFoodForm
    template_name = "food/user_food.html"
    success_url = reverse_lazy("list user food")
    initial = {"is_admin": True, "profile": None,}

    def get_context_data(self, **kwargs):
        self.get_extra_context_data()
        return super(FoodView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        form = self.get_form()

        if not profile.is_admin and not profile.is_staff:
            form.add_error("__all__", "You have no permissions to do that!")
            return self.form_invalid(form)

        return super(FoodView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        food_name = form.cleaned_data.get("name")

        if self.food_name_exists(food_name, is_admin=True):
            form.add_error("name", "Food with that name already exists")
            return self.form_invalid(form)

        return super(FoodView, self).form_valid(form)


@method_decorator(login_required, name="dispatch")
class CreateFoodView(CreateView, FoodPreSaveValidatorMixin):
    model = Food
    form_class = FoodForm
    template_name = "food/user_food_create.html"
    success_url = reverse_lazy("list user food")

    def form_valid(self, form):
        food = form.save(commit=False)
        food_name = food.name
        profile = self.request.user.profile

        if self.food_name_exists(food_name, profile=profile):
            form.add_error("name", "Food with that name already exists")
            return self.form_invalid(form)
        
        food.profile = self.request.user.profile
        food.save()
        return redirect(self.success_url)


@method_decorator(login_required, name="dispatch")
class UpdateFoodView(UpdateView, FoodPreSaveValidatorMixin):
    model = Food
    form_class = FoodForm
    pk_url_kwarg = "food_pk"
    template_name = "food/user_food_update.html"

    def get_success_url(self):
        kwargs = {"food_pk": self.kwargs.get("food_pk")}
        return reverse_lazy("food", kwargs=kwargs)
    
    def form_valid(self, form):
        food = self.get_object()
        food_name = form.cleaned_data.get("name")

        if food_name != food.name:
            if getattr(food, "is_admin"):
                kwargs = {"is_admin": True}
            else:
                kwargs = {"profile": self.request.user.profile}
    
            if self.food_name_exists(food_name, **kwargs):
                form.add_error("name", "Food with that name already exists")
                return self.form_invalid(form)
        
        return super(UpdateFoodView, self).form_valid(form)


@method_decorator(login_required, name="dispatch")
class DeleteFoodView(DeleteView):
    model = Food
    object = None
    pk_url_kwarg = "food_pk"
    success_url = reverse_lazy("list user food")

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.form_valid(None)


@method_decorator(login_required, name="dispatch")
class SaveLocallyOpenFoodView(CreateView, GetOpenFoodMixin, FoodMacrosConvertorMixin, FoodPreSaveValidatorMixin):
    model = Food
    form_class = FoodForm
    template_name = "food/save_open_food.html"

    def get_success_url(self):
        kwargs = {"food_pk": self.kwargs.get("food_pk")}
        return reverse_lazy("food", kwargs=kwargs)

    def get_context_data(self, **kwargs):
        food_data = self.get_food_by_id(self.kwargs.get("food_pk"))
        self.extra_context = food_data.copy()
        self.initial = food_data.copy()
        energy = food_data.get("energy")
        protein = food_data.get("protein")
        carbs = food_data.get("carbs")
        fat = food_data.get("fat")

        protein_percents, carbs_percents, fat_percents = self.get_percents_form_macros(
            energy, protein, carbs, fat
        )

        self.extra_context.update({
            "protein_percents": protein_percents,
            "carbs_percents": carbs_percents,
            "fat_percents": fat_percents,
        })

        return super(SaveLocallyOpenFoodView, self).get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super(SaveLocallyOpenFoodView, self).get_form_kwargs()
        kwargs["is_open_food"] = True
        kwargs["profile"] = self.request.user.profile
        return kwargs

    def form_valid(self, form):
        food = form.save(commit=False)
        food_name = form.cleaned_data.get("name")
        profile = self.request.user.profile

        if self.food_name_exists(food_name, profile=profile):
            form.add_error("name", "Food with that name already exists")
            return self.form_invalid(form)

        food.profile = self.request.user.profile
        food.save()
        self.kwargs["food_pk"] = food.pk
        return redirect(self.get_success_url())


class ListCreateFoodAPIView(APIView):
    model = Food
    __FOOD_INITIAL_DATA = {
        "energy": 0,
        "protein": 0,
        "carbs": 0,
        "fiber": 0,
        "sugars": 0,
        "fat": 0,
        "saturated_fat": 0,
        "polyunsaturated_fat": 0,
        "monounsaturated_fat": 0,
        "trans_fat": 0,
        "cholesterol": 0,
        "sodium": 0,
        "potassium": 0,
        "calcium": 0,
        "iron": 0,
        "vitamin_a": 0,
        "vitamin_c": 0,
    }

    def extend_food_data(self, data: dict) -> dict:
        extended_data = {key: 0 for key in self.__FOOD_INITIAL_DATA if key not in data}
        validated_data = QueryDict('', mutable=True)
        validated_data.update(data)
        validated_data.update(extended_data)
        return validated_data

    def get(self, request, *args, **kwargs):
        admin_food = self.model.objects.filter(is_admin=True) if request.user.profile.is_admin else []
        user_food = self.model.objects.filter(profile=request.user.profile)
        food = list(sorted(chain(admin_food, user_food), key=lambda f: f.name))
        food_serializer = FoodSerializer(food, many=True)
        return Response(food_serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = self.extend_food_data(request.data)
        food_serializer = FoodSerializer(data=data)

        if food_serializer.is_valid():
            try:
                food_serializer.save(profile=self.request.user.profile)
            except AttributeError as ex:
                return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(food_serializer.data, status=status.HTTP_201_CREATED)

        return Response(food_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetailUpdateDeleteFoodAPIView(APIView):
    model = Food
    pk_url_kwarg = "food_pk"

    def get_object(self) -> QueryDict or Response:
        try:
            return self.model.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))
        except ObjectDoesNotExist as ex:
            return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    def validate_permissions(self, food) -> bool:
        if food.is_admin and not self.request.user.profile.is_admin:
            return False
        elif not food.is_admin and food.profile != self.request.user.profile:
            return False
        return True

    def get(self, request, *args, **kwargs):
        food = self.get_object()

        if isinstance(food, Response):
            return food

        food_serializer = FoodSerializer(food)
        return Response(food_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        food = self.get_object()

        if isinstance(food, Response):
            return food

        if not self.validate_permissions(food):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        food_serializer = FoodSerializer(instance=food, data=request.data)

        if food_serializer.is_valid():
            food_serializer.save()
            return Response(food_serializer.data, status=status.HTTP_201_CREATED)

        return Response(food_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        food = self.get_object()

        if isinstance(food, Response):
            return food

        if not self.validate_permissions(food):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        food.delete()
        return Response(status=status.HTTP_200_OK)
