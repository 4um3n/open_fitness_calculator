from rest_framework import serializers
from open_fitness_calculator.food.models import Food
from open_fitness_calculator.core.mixins import FoodMacrosConvertorMixin


class FoodSerializer(serializers.ModelSerializer, FoodMacrosConvertorMixin):
    class Meta:
        model = Food
        exclude = ["profile", "is_admin"]

    def validate(self, attrs):
        required_mapper = {
            "e": int(self.initial_data.get("energy") or 0),
            "p": int(self.initial_data.get("protein") or 0),
            "c": int(self.initial_data.get("carbs") or 0),
            "f": int(self.initial_data.get("fat") or 0),
        }

        if any(required_mapper.values()):
            energy = int(sum(self.get_calories_form_macros(
                required_mapper["p"],
                required_mapper["c"],
                required_mapper["f"],
            )))
            if energy != required_mapper["e"]:
                raise serializers.ValidationError(
                    f"You set the energy to {required_mapper['e']}, but it seems to be {energy}"
                )

        return super(FoodSerializer, self).validate(attrs)
