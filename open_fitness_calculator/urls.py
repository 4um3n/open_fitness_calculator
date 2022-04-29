"""open_fitness_calculator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from open_fitness_calculator.settings import MEDIA_URL, MEDIA_ROOT

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('accounts/', include('allauth.urls')),
                  path('api/auth/', include('djoser.urls.authtoken')),
                  path('user/auth/', include("open_fitness_calculator.fitness_calculator_auth.urls")),
                  path('', include("open_fitness_calculator.core.urls")),
                  path('profile/', include("open_fitness_calculator.profiles.urls")),
                  path('food/', include("open_fitness_calculator.food.urls")),
                  path('exercises/', include("open_fitness_calculator.exercises.urls")),
                  path('diary/', include("open_fitness_calculator.diary.urls")),
              ] + static(MEDIA_URL, document_root=MEDIA_ROOT)
