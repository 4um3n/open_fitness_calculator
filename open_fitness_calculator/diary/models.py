import datetime
from django.db import models
from cloudinary import models as cloudinary_models
from open_fitness_calculator.profiles.models import Profile
from open_fitness_calculator.core.mixins import BaseDiaryMacrosPieChartMixin, BaseDiaryCaloriesPieChartMixin


class Diary(models.Model):
    name = models.CharField(
        max_length=100,
        default=datetime.date.today,
        blank=True
    )
    profile = models.ForeignKey(
        to=Profile,
        on_delete=models.CASCADE,
    )
    is_completed = models.BooleanField(
        default=False,
    )
    start_date = models.DateField(
        default=datetime.date.today,
    )
    end_date = models.DateField(
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = "Diaries"

    @property
    def calories(self) -> int:
        return self.profile.dailynutrients.daily_calories

    @property
    def eaten_calories(self) -> int:
        return sum([diary_food.get_eaten_calories() for diary_food in self.diaryfood_set.all()])

    @property
    def exercises_calories(self) -> int:
        return sum([diary_exercise.get_burned_calories() for diary_exercise in self.diaryexercise_set.all()])

    @property
    def remaining_calories(self) -> int:
        return self.calories - self.eaten_calories + self.exercises_calories

    @property
    def meals_calories(self) -> tuple:
        t_cals, b_cals, l_cals, d_cals, s_cals = 0, 0, 0, 0, 0

        for meal in self.diaryfood_set.all():
            t_cals += meal.food.energy * meal.quantity / 100
            b_cals += meal.food.energy * meal.quantity / 100 if meal.meal_type == "Breakfast" else 0
            l_cals += meal.food.energy * meal.quantity / 100 if meal.meal_type == "Lunch" else 0
            d_cals += meal.food.energy * meal.quantity / 100 if meal.meal_type == "Dinner" else 0
            s_cals += meal.food.energy * meal.quantity / 100 if meal.meal_type == "Snack" else 0

        return t_cals, b_cals, l_cals, d_cals, s_cals

    @property
    def meals_base_macros(self) -> tuple:
        protein_grams, carbs_grams, fat_grams = 0, 0, 0

        for meal in self.diaryfood_set.all():
            protein_grams += meal.food.protein * meal.quantity / 100
            carbs_grams += meal.food.carbs * meal.quantity / 100
            fat_grams += meal.food.fat * meal.quantity / 100

        return protein_grams, carbs_grams, fat_grams

    @property
    def macros(self) -> dict:
        return {
            "protein": self.profile.dailynutrients.daily_protein,
            "carbohydrates": self.profile.dailynutrients.daily_carbs,
            "fibers": self.profile.dailynutrients.daily_fiber,
            "sugars": self.profile.dailynutrients.daily_sugars,
            "fat": self.profile.dailynutrients.daily_fat,
            "saturated": self.profile.dailynutrients.daily_saturated_fat,
            "monounsaturated": self.profile.dailynutrients.daily_polyunsaturated_fat,
            "polyunsaturated": self.profile.dailynutrients.daily_monounsaturated_fat,
            "trans": self.profile.dailynutrients.daily_trans_fat,
        }

    @property
    def micros(self) -> dict:
        return {
            "cholesterol": self.profile.dailynutrients.daily_cholesterol,
            "sodium": self.profile.dailynutrients.daily_sodium,
            "potassium": self.profile.dailynutrients.daily_potassium,
            "vitamin a": self.profile.dailynutrients.daily_vitamin_a,
            "vitamin c": self.profile.dailynutrients.daily_vitamin_c,
            "calcium": self.profile.dailynutrients.daily_calcium,
            "iron": self.profile.dailynutrients.daily_iron,
        }

    @property
    def eaten_macros(self) -> dict:
        eaten_macros = {
            "protein": 0,
            "carbohydrates": 0,
            "fibers": 0,
            "sugars": 0,
            "fat": 0,
            "saturated": 0,
            "polyunsaturated": 0,
            "monounsaturated": 0,
            "trans": 0,
        }

        for meal in self.diaryfood_set.all():
            eaten_macros["protein"] += meal.food.protein * meal.quantity / 100
            eaten_macros["carbohydrates"] += meal.food.carbs * meal.quantity / 100
            eaten_macros["fibers"] += meal.food.fiber * meal.quantity / 100
            eaten_macros["sugars"] += meal.food.sugars * meal.quantity / 100
            eaten_macros["fat"] += meal.food.fat * meal.quantity / 100
            eaten_macros["saturated"] += meal.food.saturated_fat * meal.quantity / 100
            eaten_macros["monounsaturated"] += meal.food.monounsaturated_fat * meal.quantity / 100
            eaten_macros["polyunsaturated"] += meal.food.polyunsaturated_fat * meal.quantity / 100
            eaten_macros["trans"] += meal.food.trans_fat * meal.quantity / 100

        return eaten_macros

    @property
    def eaten_micros(self) -> dict:
        eaten_micros = {
            "cholesterol": 0,
            "sodium": 0,
            "potassium": 0,
            "vitamin a": 0,
            "vitamin c": 0,
            "calcium": 0,
            "iron": 0,
        }

        for meal in self.diaryfood_set.all():
            eaten_micros["cholesterol"] += meal.food.cholesterol * meal.quantity / 100
            eaten_micros["sodium"] += meal.food.sodium * meal.quantity / 100
            eaten_micros["potassium"] += meal.food.potassium * meal.quantity / 100
            eaten_micros["vitamin a"] += meal.food.vitamin_a * meal.quantity / 100
            eaten_micros["vitamin c"] += meal.food.vitamin_c * meal.quantity / 100
            eaten_micros["calcium"] += meal.food.calcium * meal.quantity / 100
            eaten_micros["iron"] += meal.food.iron * meal.quantity / 100

        return eaten_micros

    @property
    def remaining_macros(self) -> dict:
        macros = self.macros
        eaten_macros = self.eaten_macros
        return {name: value - eaten_macros[name] for name, value in macros.items()}

    @property
    def remaining_micros(self) -> dict:
        micros = self.micros
        eaten_micros = self.eaten_micros
        return {name: value - eaten_micros[name] for name, value in micros.items()}

    def get_meals_calories_percents(self) -> tuple:
        total, breakfast, lunch, dinner, snack = self.meals_calories

        if total <= 0:
            return 0, 0, 0, 0

        breakfast_percents = breakfast / total * 100 if breakfast > 0 else 0
        lunch_percents = lunch / total * 100 if lunch > 0 else 0
        dinner_percents = dinner / total * 100 if dinner > 0 else 0
        snack_percents = snack / total * 100 if snack > 0 else 0
        return breakfast_percents, lunch_percents, dinner_percents, snack_percents

    def get_meals_macros_percents(self) -> tuple:
        if self.eaten_calories <= 0:
            return 0, 0, 0

        cals = self.eaten_calories
        protein, carbs, fat = self.meals_base_macros
        protein *= 4
        carbs *= 4
        fat *= 9

        macros_percents = {
            "p": int(protein / cals * 100) if protein else 0,
            "c": int(carbs / cals * 100) if carbs else 0,
            "f": int(fat / cals * 100) if fat else 0,
        }

        return int(macros_percents["p"]), int(macros_percents["c"]), int(macros_percents["f"])

    def __str__(self):
        return f"{self.name}"


class CaloriesPieChart(models.Model, BaseDiaryCaloriesPieChartMixin):
    diary = models.OneToOneField(
        to=Diary,
        on_delete=models.CASCADE,
    )

    image = cloudinary_models.CloudinaryField(
        "Image",
        overwrite=True,
        resource_type="image",
        transformation={"quality": "auto:eco"},
        format="png",
    )

    @property
    def name(self):
        return self.diary.pk

    @classmethod
    def __reset_image(cls, pk, new_image):
        cls.objects.filter(pk=pk).update(image=new_image)

    def reset_pie_chart(self):
        self.create_pie_chart()
        new_pie_chart = self._upload_new_pie_chart()
        self.__reset_image(self.pk, new_pie_chart)
        self._delete_unused_local_pie_chart()

    def delete_cloudinary_pie_chart(self):
        self._delete_unused_cloudinary_pie_chart()

    def __str__(self):
        return f"{self.diary}"


class MacrosPieChart(models.Model, BaseDiaryMacrosPieChartMixin):
    diary = models.OneToOneField(
        to=Diary,
        on_delete=models.CASCADE,
    )

    image = cloudinary_models.CloudinaryField(
        "Image",
        overwrite=True,
        resource_type="image",
        transformation={"quality": "auto:eco"},
        format="png",
    )

    @property
    def name(self):
        return self.diary.pk

    @classmethod
    def __reset_image(cls, pk, new_image):
        cls.objects.filter(pk=pk).update(image=new_image)

    def reset_pie_chart(self):
        self.create_pie_chart()
        new_pie_chart = self._upload_new_pie_chart()
        self.__reset_image(self.pk, new_pie_chart)
        self._delete_unused_local_pie_chart()

    def delete_cloudinary_pie_chart(self):
        self._delete_unused_cloudinary_pie_chart()

    def __str__(self):
        return f"{self.diary}"
