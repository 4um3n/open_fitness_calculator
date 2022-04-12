from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView, ListView

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from open_fitness_calculator.food.forms import SearchFoodForm
from open_fitness_calculator.core.mixins import SearchOpenFoodMixin


@method_decorator(login_required, name="dispatch")
class HomeView(ListView, FormView, SearchOpenFoodMixin):
    form_class = SearchFoodForm
    template_name = "core/home.html"
    success_url = reverse_lazy("home")
    paginate_by = 6
    object_list = []

    def get_food(self):
        return self.kwargs.get("food") or \
               self.request.session.get("last_food") or []

    def get_queryset(self):
        if self.kwargs.get("page") is not None:
            return self.kwargs.get("food") or []

        if self.request.GET.get("page") is not None:
            return self.get_food()
        else:
            self.request.session["last_food"] = None
            self.kwargs["page"] = None
            return []

    def get_context_data(self, **kwargs):
        food = self.get_queryset()
        self.request.session["last_food"] = food
        diary = self.request.user.profile.diary_set.get(is_completed=False)
        paginator, page, queryset, is_paginated = self.paginate_queryset(food, self.paginate_by)

        self.extra_context = {
            'page_obj': page,
            "food": page.object_list,
            "user": self.request.user,
            "calories": int(diary.calories),
            "eaten_calories": int(diary.eaten_calories),
            "exercises_calories": int(diary.exercises_calories),
            "remaining_calories": int(diary.remaining_calories),
        }

        return super(HomeView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        food_data = self.get_food_by_searched_string(
            form.cleaned_data["searched_string"],
            form.cleaned_data["accurate_search"],
        )

        self.kwargs["page"] = 1
        self.kwargs["food"] = food_data
        return self.render_to_response(context=self.get_context_data())


class StatusAPIView(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)
