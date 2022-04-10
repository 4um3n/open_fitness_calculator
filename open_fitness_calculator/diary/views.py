import datetime
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import UpdateView, RedirectView, ListView

from open_fitness_calculator.diary.models import Diary
from open_fitness_calculator.diary.forms import DiaryForm
from open_fitness_calculator.profiles.forms import MacrosPercentsForm


@method_decorator(login_required, name="dispatch")
class DiaryBaseView(ListView):
    model = Diary
    paginate_by = 1
    diary_object = None
    delete_diary_redirect_url = None

    def get(self, request, *args, **kwargs):
        self.get_extra_context_data()
        self.request.session["delete_diary_redirect_url"] = self.delete_diary_redirect_url or "profile diary"
        return super(DiaryBaseView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.get_extra_context_data()
        return super(DiaryBaseView, self).post(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(profile=self.request.user.profile)

    def get_page(self) -> int:
        return self.request.GET.get("page") or \
               self.request.session.get("last_page") or \
               self.get_queryset().count()

    def get_extra_context_data(self, object_list=None, **kwargs):
        page = self.get_page()
        self.kwargs["page"] = page
        self.request.session["last_page"] = page

        queryset = self.get_queryset()
        page_size = self.get_paginate_by(queryset)
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
        self.diary_object = page.object_list.get()

        self.extra_context = {
            'paginator': paginator,
            'page_obj': page,
            "diary": self.diary_object,
        }
        return self.extra_context


class DiaryView(DiaryBaseView, UpdateView):
    form_class = DiaryForm
    template_name = "diary/diary.html"
    success_url = reverse_lazy("profile diary")
    delete_diary_redirect_url = "profile diary"

    def get_object(self, queryset=None):
        return self.diary_object

    def get_context_data(self, *, object_list=None, **kwargs):
        diary = self.diary_object
        meals = diary.diaryfood_set.all()
        exercises = diary.diaryexercise_set.all()

        meals_mapper = {
            "Breakfast": [meal for meal in meals if meal.meal_type == "Breakfast"],
            "Lunch": [meal for meal in meals if meal.meal_type == "Lunch"],
            "Dinner": [meal for meal in meals if meal.meal_type == "Dinner"],
            "Snack": [meal for meal in meals if meal.meal_type == "Snack"],
        }

        self.extra_context.update({
            "form": self.get_form(),
            "exercises": exercises,
            "meals_mapper": meals_mapper,
            "post_button_value": "Update Diary" if diary.is_completed else "Complete Diary",
        })

        return self.extra_context

    def get_initial(self):
        return {
            "is_completed": True,
            "end_date": datetime.date.today(),
            "name": self.get_object().name
        }


@method_decorator(never_cache, name="dispatch")
class EnergyView(DiaryBaseView):
    fields = {}
    template_name = "diary/energy.html"
    delete_diary_redirect_url = "profile energy"

    def get_object(self, queryset=None):
        return self.diary_object

    def get_context_data(self, **kwargs):
        diary = self.diary_object
        total_cals, b_cals, l_cals, d_cals, s_cals = diary.meals_calories
        b_percents, l_percents, d_percents, s_percents = diary.get_meals_calories_percents()

        self.extra_context.update({
            "eaten_cals": total_cals - diary.exercises_calories,
            "goal_cals": diary.calories,
            "remaining_cals": diary.remaining_calories,
            "breakfast_cals": b_cals,
            "lunch_cals": l_cals,
            "dinner_cals": d_cals,
            "snacks_cals": s_cals,
            "breakfast_percents": b_percents,
            "lunch_percents": l_percents,
            "dinner_percents": d_percents,
            "snacks_percents": s_percents,
        })

        return self.extra_context


@method_decorator(never_cache, name="dispatch")
class NutrientsView(DiaryBaseView):
    fields = {}
    template_name = "diary/nutrients.html"
    delete_diary_redirect_url = "profile nutrients"

    def get_object(self, queryset=None):
        return self.diary_object

    def get_context_data(self, **kwargs):
        diary = self.diary_object
        goal_nutrients = diary.macros
        eaten_nutrients = diary.eaten_macros
        remaining_nutrients = diary.remaining_macros
        goal_nutrients.update(diary.micros)
        eaten_nutrients.update(diary.eaten_micros)
        remaining_nutrients.update(diary.remaining_micros)

        nutrients = {
            nutrient_name: (eaten_nutrients[nutrient_name], goal_nutrient, remaining_nutrients[nutrient_name])
            for nutrient_name, goal_nutrient in goal_nutrients.items()
        }

        self.extra_context.update({
            "nutrients": nutrients,
            "mg_fields": ("cholesterol", "sodium", "potassium"),
            "percents_fields": ("vitamin a", "vitamin c", "calcium", "iron"),
        })

        return self.extra_context


@method_decorator(never_cache, name="dispatch")
class MacrosView(DiaryBaseView, UpdateView):
    object_list = None
    form_class = MacrosPercentsForm
    template_name = "diary/macros.html"
    success_url = reverse_lazy("profile macros")
    delete_diary_redirect_url = "profile macros"

    def get_object(self, queryset=None):
        return self.request.user.profile.macrospercents

    def get_context_data(self, **kwargs):
        diary = self.diary_object
        p_grams, c_grams, f_grams = diary.meals_macros
        eaten_p_percents, eaten_c_percents, eaten_f_percents = diary.get_meals_macros_percents()

        self.extra_context.update({
            "form": self.get_form(),
            "protein_grams": p_grams,
            "carbs_grams": c_grams,
            "fat_grams": f_grams,
            "eaten_protein_percent": eaten_p_percents,
            "eaten_carbs_percents": eaten_c_percents,
            "eaten_fat_percents": eaten_f_percents,
        })

        return self.extra_context

    def get_initial(self):
        return self.get_object().__dict__.copy()


@method_decorator(login_required, name="dispatch")
class DiaryDeleteView(RedirectView):
    model = Diary

    def get_redirect_url(self, *args, **kwargs):
        url = self.request.session.get("delete_diary_redirect_url") or "profile diary"
        return reverse_lazy(url)

    def get_object(self):
        try:
            return self.model.objects.get(pk=self.kwargs.get("diary_pk"))
        except ObjectDoesNotExist:
            return get_object_or_404(self.model, is_completed=False)

    def get(self, request, *args, **kwargs):
        self.get_object().delete()
        return super(DiaryDeleteView, self).get(request, *args, **kwargs)
