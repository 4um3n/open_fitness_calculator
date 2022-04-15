from django.urls import path
from open_fitness_calculator.core.views import HomeView, StatusAPIView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("api/status/", StatusAPIView.as_view()),
]
