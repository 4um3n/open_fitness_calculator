from django.contrib import admin
from open_fitness_calculator.diary.models import Diary, CaloriesPieChart, MacrosPieChart


@admin.register(Diary)
class DiaryAdmin(admin.ModelAdmin):
    pass


@admin.register(CaloriesPieChart)
class CaloriesPieChartAdmin(admin.ModelAdmin):
    pass


@admin.register(MacrosPieChart)
class MacrosPieChartAdmin(admin.ModelAdmin):
    pass
