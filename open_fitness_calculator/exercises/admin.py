from django.contrib import admin

from open_fitness_calculator.exercises.models import Exercise, DiaryExercise


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    pass


@admin.register(DiaryExercise)
class DiaryExerciseAdmin(admin.ModelAdmin):
    pass
