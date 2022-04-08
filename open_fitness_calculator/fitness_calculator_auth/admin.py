from django.contrib import admin
from django.contrib.admin import register
from open_fitness_calculator.fitness_calculator_auth.models import FitnessCalculatorUser


@register(FitnessCalculatorUser)
class FitnessCalculatorUserAdmin(admin.ModelAdmin):
    pass
