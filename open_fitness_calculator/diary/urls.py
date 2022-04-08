from django.urls import path
from open_fitness_calculator.diary.views import DiaryView,  DiaryDeleteView, \
    EnergyView, NutrientsView, MacrosView

urlpatterns = [
    path(
        "diary/",
        DiaryView.as_view(),
        name="profile diary"
    ),
    path(
        "energy/",
        EnergyView.as_view(),
        name="profile energy"
    ),
    path(
        "nutrients/",
        NutrientsView.as_view(),
        name="profile nutrients"
    ),
    path(
        "macros/",
        MacrosView.as_view(),
        name="profile macros"
    ),
    path(
        "diary-delete/<int:diary_pk>",
        DiaryDeleteView.as_view(),
        name="profile delete diary"
    ),
]
