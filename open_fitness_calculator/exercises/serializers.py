from rest_framework import serializers

from open_fitness_calculator.exercises.models import Exercise


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ["name", "unit", "burned_calories_per_unit", "id"]
