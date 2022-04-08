from django.urls import path
from open_fitness_calculator.food.views import LogFoodView, DiaryFoodView, ListAvailableFoodView, FoodView, \
    DeleteFoodFromDiaryView, ListUserFoodView, CreateFoodView, UpdateFoodView, DeleteFoodView, \
    SaveLocallyOpenFoodView, ListCreateFoodAPIView, DetailUpdateDeleteFoodAPIView

urlpatterns = [
    path(
        '<int:food_pk>/<int:diary_pk>/<str:meal>',
        LogFoodView.as_view(),
        name='food'
    ),
    path(
        'meal/<int:diary_pk>/<int:meal_pk>/',
        DiaryFoodView.as_view(),
        name='meal food'
    ),
    path(
        'delete-from-diary/<int:diary_pk>/<int:meal_pk>/',
        DeleteFoodFromDiaryView.as_view(),
        name='delete food from diary'
    ),
    path(
        'list-available-food/<int:diary_pk>/<str:meal>/',
        ListAvailableFoodView.as_view(),
        name='list available food'
    ),
    path(
        'list-user-available-food/',
        ListUserFoodView.as_view(),
        name='list user food'
    ),
    path(
        'user-food/<int:food_pk>/',
        FoodView.as_view(),
        name='user food'
    ),
    path(
        'create-user-food/',
        CreateFoodView.as_view(),
        name='create user food'
    ),
    path(
        'update-user-food/<int:food_pk>',
        UpdateFoodView.as_view(),
        name='update user food'
    ),
    path(
        'delete-user-food/<int:food_pk>/',
        DeleteFoodView.as_view(),
        name='delete user food'
    ),
    path(
        'save-locally-open-food/<int:food_pk>',
        SaveLocallyOpenFoodView.as_view(),
        name="save locally open food",
    ),
    path(
        "api/",
        ListCreateFoodAPIView.as_view()
    ),
    path(
        "api/<int:food_pk>",
        DetailUpdateDeleteFoodAPIView.as_view()
    ),
]
