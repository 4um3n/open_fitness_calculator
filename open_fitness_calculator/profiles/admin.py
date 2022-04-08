from django.contrib import admin
from django.contrib.admin import register
from open_fitness_calculator.profiles.models import Profile, DailyNutrients, Goal, MacrosPercents


@register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@register(MacrosPercents)
class MacrosPercentsAdmin(admin.ModelAdmin):
    pass


@register(Goal)
class GoalsAdmin(admin.ModelAdmin):
    pass


@register(DailyNutrients)
class DailyNutrientsAdmin(admin.ModelAdmin):
    pass
