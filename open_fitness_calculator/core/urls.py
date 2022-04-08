from django.urls import path
from open_fitness_calculator.core.views import HomeView, StatusAPIView
from open_fitness_calculator.core import signals

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("api/status/", StatusAPIView.as_view()),
]
