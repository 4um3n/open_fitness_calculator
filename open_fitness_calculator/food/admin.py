from django.contrib import admin
from django.contrib.admin import register
from open_fitness_calculator.food.models import FoodCategory, Food, DiaryFood, FoodPieChart


@register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    pass


@register(FoodPieChart)
class FoodPieChartAdmin(admin.ModelAdmin):
    pass


@register(Food)
class FoodAdmin(admin.ModelAdmin):
    pass


@register(DiaryFood)
class MealAdmin(admin.ModelAdmin):
    pass
