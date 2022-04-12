from itertools import chain
from rest_framework import status
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import FormView, DetailView, UpdateView, RedirectView, CreateView, DeleteView

from open_fitness_calculator.diary.models import Diary
from open_fitness_calculator.exercises.models import DiaryExercise, Exercise
from open_fitness_calculator.exercises.serializers import ExerciseSerializer
from open_fitness_calculator.exercises.forms import ExerciseQuantityForm, AdminExerciseForm, SearchExerciseForm, \
    ExerciseForm


@method_decorator(login_required, name="dispatch")
class LogExerciseView(DetailView, FormView):
    form_class = ExerciseQuantityForm
    model = Exercise
    pk_url_kwarg = "exercise_pk"
    template_name = "exercises/log_exercise.html"
    success_url = reverse_lazy("profile diary")

    def form_valid(self, form):
        diary = get_object_or_404(Diary, pk=self.kwargs.get("diary_pk"))
        DiaryExercise.objects.create(
            diary=diary,
            exercise=self.get_object(),
            quantity=form.cleaned_data.get("quantity"),
        ).save()
        return super(LogExerciseView, self).form_valid(form)


@method_decorator(login_required, name="dispatch")
class DiaryExerciseView(UpdateView):
    model = DiaryExercise
    form_class = ExerciseQuantityForm
    pk_url_kwarg = "exercise_pk"
    template_name = "exercises/diary_exercise.html"

    def get_success_url(self):
        kwargs = {
            "diary_pk": self.kwargs.get("diary_pk"),
            "exercise_pk": self.kwargs.get("exercise_pk"),
        }
        return reverse_lazy("diary exercise", kwargs=kwargs)

    def get_context_data(self, **kwargs):
        diary_exercise = self.get_object()
        self.extra_context = {
            "diary_exercise": diary_exercise,
            "burned_calories": diary_exercise.exercise.burned_calories_per_unit * diary_exercise.quantity,
            "diary_pk": self.kwargs.get("diary_pk"),
        }
        return super(DiaryExerciseView, self).get_context_data(**kwargs)


@method_decorator(login_required, name="dispatch")
class DeleteExerciseFromDiaryView(RedirectView):
    url = reverse_lazy("profile diary")

    def get(self, request, *args, **kwargs):
        exercise = get_object_or_404(DiaryExercise, pk=self.kwargs.get("exercise_pk"))
        exercise.delete()
        return super(DeleteExerciseFromDiaryView, self).get(request, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class ListAvailableExercisesView(FormView):
    form_class = SearchExerciseForm
    template_name = "exercises/list_available_exercises.html"

    def get_exercises(self):
        exercises = Exercise.objects.filter(is_admin=True)
        user_exercises = Exercise.objects.filter(profile=self.request.user.profile)
        return list(sorted(chain(exercises, user_exercises), key=lambda e: e.name))

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(exercises=self.get_exercises()))

    def get_context_data(self, **kwargs):
        exercises = kwargs.get("exercises")
        self.extra_context = {
            "diary_pk": self.kwargs.get("diary_pk"),
            "exercises": exercises if exercises is not None else self.get_exercises(),
        }
        return super(ListAvailableExercisesView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        exercise = self.get_exercises()
        searched_str = form.cleaned_data.get("searched_string")
        searched_str = searched_str.lower() if searched_str else ""
        exercises = [e for e in exercise if e.name.lower() in searched_str or searched_str in e.name.lower()]
        return self.render_to_response(self.get_context_data(exercises=exercises))


@method_decorator(login_required, name="dispatch")
class ListUserExercisesView(FormView):
    form_class = SearchExerciseForm
    template_name = "exercises/list_user_exercises.html"

    def get_exercises(self):
        user_exercises = Exercise.objects.filter(profile=self.request.user.profile)
        admin_exercises = Exercise.objects.filter(is_admin=True)
        return list(sorted(chain(user_exercises, admin_exercises), key=lambda e: e.name))

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(exercises=self.get_exercises()))

    def get_context_data(self, **kwargs):
        exercises = kwargs.get("exercises")
        exercises = exercises if exercises is not None else self.get_exercises()
        self.extra_context = {"exercises": exercises}
        return super(ListUserExercisesView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        user_exercises = self.get_exercises()
        searched_str = form.cleaned_data.get("searched_string")
        searched_str = searched_str.lower() if searched_str else ""
        exercises = [e for e in user_exercises if e.name.lower() in searched_str or searched_str in e.name.lower()]
        return self.render_to_response(self.get_context_data(exercises=exercises))


@method_decorator(login_required, name="dispatch")
class ExerciseView(DetailView, UpdateView):
    object = None
    model = Exercise
    pk_url_kwarg = "exercise_pk"
    form_class = AdminExerciseForm
    template_name = "exercises/user_exercise.html"
    success_url = reverse_lazy("list user exercises")
    initial = {
        "is_admin": True,
        "profile": None,
    }

    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        form = self.get_form()

        if not profile.is_admin and not profile.is_staff:
            form.add_error("__all__", "You have no permissions to do that!")
            return self.form_invalid(form)

        return super(ExerciseView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        exercises_names = [e.name.lower() for e in Exercise.objects.filter(is_admin=True)]

        if form.cleaned_data.get("name").lower() in exercises_names:
            form.add_error("__all__", "Exercise with this name already exist!")
            return self.form_invalid(form)

        return super(ExerciseView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        self.extra_context = {"exercise": self.get_object()}
        return super(ExerciseView, self).get_context_data(**kwargs)


@method_decorator(login_required, name="dispatch")
class CreateUserExerciseView(CreateView):
    form_class = ExerciseForm
    template_name = "exercises/user_exercise_create.html"
    success_url = reverse_lazy("list user exercises")

    def form_valid(self, form):
        exercise = form.save(commit=False)
        exercise.profile = self.request.user.profile
        exercise.save()
        return redirect(self.success_url)


@method_decorator(login_required, name="dispatch")
class UpdateUserExerciseView(UpdateView):
    model = Exercise
    form_class = ExerciseForm
    pk_url_kwarg = "exercise_pk"
    template_name = "exercises/user_exercise_update.html"

    def get_success_url(self):
        kwargs = {"exercise_pk": self.kwargs.get("exercise_pk")}
        return reverse_lazy("exercise", kwargs=kwargs)


@method_decorator(login_required, name="dispatch")
class DeleteUserExerciseView(DeleteView):
    model = Exercise
    object = None
    pk_url_kwarg = "exercise_pk"
    success_url = reverse_lazy("list user exercises")

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.form_valid(None)


class ListCreateExerciseAPIView(APIView):
    model = Exercise

    def get(self, request, *args, **kwargs):
        admin_exercises = self.model.objects.filter(is_admin=True) if request.user.profile.is_admin else []
        user_exercises = self.model.objects.filter(profile=request.user.profile)
        exercises = list(sorted(chain(admin_exercises, user_exercises), key=lambda f: f.name))
        exercise_serializer = ExerciseSerializer(exercises, many=True)
        return Response(exercise_serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        exercise_serializer = ExerciseSerializer(data=request.data)

        if exercise_serializer.is_valid():
            try:
                exercise_serializer.save(profile=self.request.user.profile)
            except AttributeError as ex:
                return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(exercise_serializer.data, status=status.HTTP_201_CREATED)

        return Response(exercise_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetailUpdateDeleteExerciseAPIView(APIView):
    model = Exercise
    pk_url_kwarg = "exercise_pk"

    def get_object(self) -> QueryDict or Response:
        try:
            return self.model.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))
        except ObjectDoesNotExist as ex:
            return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    def validate_permissions(self, exercise) -> bool:
        if exercise.is_admin and not self.request.user.profile.is_admin:
            return False
        elif not exercise.is_admin and exercise.profile != self.request.user.profile:
            return False
        return True

    def get(self, request, *args, **kwargs):
        exercise = self.get_object()
        if isinstance(exercise, Response):
            return exercise

        food_serializer = ExerciseSerializer(exercise)
        return Response(food_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        exercise = self.get_object()
        if isinstance(exercise, Response):
            return exercise

        if not self.validate_permissions(exercise):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        exercise_serializer = ExerciseSerializer(instance=exercise, data=request.data)

        if exercise_serializer.is_valid():
            exercise_serializer.save()
            return Response(exercise_serializer.data, status=status.HTTP_201_CREATED)

        return Response(exercise_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        exercise = self.get_object()
        if isinstance(exercise, Response):
            return exercise

        if not self.validate_permissions(exercise):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        exercise.delete()
        return Response(status=status.HTTP_200_OK)
