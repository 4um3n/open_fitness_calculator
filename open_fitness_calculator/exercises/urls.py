from django.urls import path

from open_fitness_calculator.exercises.views import LogExerciseView, UserExerciseView, DiaryExerciseView, \
    DeleteExerciseFromDiaryView, ListAvailableExercisesView, ListUserExercisesView, CreateUserExerciseView, \
    UpdateUserExerciseView, DeleteUserExerciseView, ListCreateExerciseAPIView, DetailUpdateDeleteExerciseAPIView

urlpatterns = [
    path(
        '<int:exercise_pk>/<int:diary_pk>/',
        LogExerciseView.as_view(),
        name='exercise'
    ),
    path(
        'diary-exercise/<int:diary_pk>/<int:exercise_pk>/',
        DiaryExerciseView.as_view(),
        name='diary exercise'
    ),
    path(
        'delete-from-diary/<int:diary_pk>/<int:exercise_pk>/',
        DeleteExerciseFromDiaryView.as_view(),
        name='delete exercise from diary'
    ),
    path(
        'list-available-exercises/<int:diary_pk>/',
        ListAvailableExercisesView.as_view(),
        name='list available exercises'
    ),
    path(
        'list-user-available-exercises/',
        ListUserExercisesView.as_view(),
        name='list user exercises'
    ),
    path(
        'user-exercise/<int:exercise_pk>/',
        UserExerciseView.as_view(),
        name='user exercise'
    ),
    path(
        'create-user-exercise/',
        CreateUserExerciseView.as_view(),
        name='create user exercise'
    ),
    path(
        'update-user-exercise/<int:exercise_pk>',
        UpdateUserExerciseView.as_view(),
        name='update user exercise'
    ),
    path(
        'delete-user-exercise/<int:exercise_pk>/',
        DeleteUserExerciseView.as_view(),
        name='delete user exercise'
    ),
    path(
        "api/",
        ListCreateExerciseAPIView.as_view()
    ),
    path(
        "api/<int:exercise_pk>",
        DetailUpdateDeleteExerciseAPIView.as_view()
    ),
]

