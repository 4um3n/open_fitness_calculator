import os
from collections import deque

import requests
from matplotlib import pyplot as plt
from open_fitness_calculator.settings import BASE_DIR


class FoodMacrosConvertorMixin:
    energy, protein, carbs, fat = 0, 0, 0, 0

    def get_calories_form_macros(self, protein_grams=None, carbs_grams=None, fat_grams=None):
        protein_grams = protein_grams or self.protein
        carbs_grams = carbs_grams or self.carbs
        fat_grams = fat_grams or self.fat

        protein_calories = protein_grams * 4 if protein_grams and protein_grams > 0 else 0
        carbs_calories = carbs_grams * 4 if carbs_grams and carbs_grams > 0 else 0
        fat_calories = fat_grams * 9 if fat_grams and fat_grams > 0 else 0

        return protein_calories, carbs_calories, fat_calories

    def get_percents_form_macros(self, energy=None, protein_grams=None, carbs_grams=None, fat_grams=None):
        energy = energy or self.energy
        p_calories, c_calories, f_calories = self.get_calories_form_macros(protein_grams, carbs_grams, fat_grams)
        percents_keys = deque(["p", "c", "f"])

        percents = {
            "p": round(p_calories / energy * 100, 2) if energy and energy > 0 and p_calories > 0 else 0,
            "c": round(c_calories / energy * 100, 2) if energy and energy > 0 and c_calories > 0 else 0,
            "f": round(f_calories / energy * 100, 2) if energy and energy > 0 and f_calories > 0 else 0,
        }

        if any(percents.values()):
            while sum(percents.values()) > 100:
                if percents[percents_keys[0]] > 0:
                    percents[percents_keys[0]] -= 0.01
                percents_keys.append(percents_keys.popleft())

            while sum(percents.values()) < 100:
                if percents[percents_keys[0]] > 0:
                    percents[percents_keys[0]] += 0.01
                percents_keys.append(percents_keys.popleft())

        return round(percents["p"], 2), round(percents["c"], 2), round(percents["f"], 2)


class DailyCaloriesCalculatorMixin:
    profile = None
    daily_calories = 0

    ACTIVITY_LEVEL_MAPPER = {
        "not_active": lambda x: x * 1.2,
        "low": lambda x: x * 1.375,
        "medium": lambda x: x * 1.55,
        "high": lambda x: x * 1.725,
    }
    GOAL_MAPPER = {
        "loose": lambda x, y: x - x * 0.20 - y / 2,
        "maintain": lambda x, y: x,
        "gain": lambda x, y: x + x * 0.20 + y / 3,
    }

    @property
    def macros_percents(self):
        if self.profile is not None:
            return self.profile.macrospercents.percents

    def _calculate_daily_calories(self):
        """
        Calculate daily Resting Energy Expenditure (REE)
        and Total Energy Expenditure (TEE)

        return: Total Energy Expenditure (TEE)
        """
        ree = 10 * self.profile.weight + 6.25 * self.profile.height - 5 * self.profile.age
        ree = ree - 161 if self.profile.gender == "female" else ree + 5
        tee = self.ACTIVITY_LEVEL_MAPPER[self.profile.goal.activity_level](ree)
        tee = self.GOAL_MAPPER[self.profile.goal.goal](tee, self.profile.goal.per_week)
        return tee

    def _calculate_daily_nutrients(self):
        protein_percents, carbs_percents, fat_percents = self.macros_percents
        protein_grams = (self.daily_calories * protein_percents) // 4

        carbs_grams = (self.daily_calories * carbs_percents) // 4
        carbs_sugar_grams = (self.daily_calories * 0.09) // 4 if carbs_grams else 0
        fiber = 38 if self.profile.gender == "male" else 25

        fat_grams = (self.daily_calories * fat_percents) // 9
        fat_saturated_grams = (self.daily_calories * 0.06) // 9 if fat_grams else 0
        return protein_grams, carbs_grams, carbs_sugar_grams, fiber, fat_grams, fat_saturated_grams


class PieChartCreationMixin:
    full_file_path = None
    sizes = None

    def create_pie_chart(self):
        save_path, sizes = self.full_file_path, self.sizes()
        plt.rcParams["figure.figsize"] = (2.5, 2.5)
        colors = "#017250FF", "#FF8000FF", "#FF0062FF", "#004378FF"

        sizes = [int(s) for s in sizes if s >= 0]
        if sum(sizes) <= 0 or len(sizes) > 4:
            sizes = [1]
            colors = ["#707070FF"]

        explode = [0.1 for _ in range(len(sizes))]

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, colors=colors, explode=explode, startangle=90)
        plt.savefig(save_path, transparent=True)


class BasePieChartMixin(PieChartCreationMixin):
    pk = None
    name = None
    image = None
    objects = None
    images_directory = None

    @property
    def file_name(self):
        return f"{self.pk}_{self.name}.png"

    @property
    def file_path(self):
        return os.path.join("images", f"{self.images_directory}", self.file_name)

    @property
    def default_file_path(self):
        return os.path.join("images", f"{self.images_directory}", "default/default.png")

    @property
    def full_file_path(self):
        return os.path.join(BASE_DIR, "media", "images", f"{self.images_directory}", self.file_name)

    def get_file_path(self):
        if not os.path.isfile(self.full_file_path):
            return self.default_file_path

        return self.file_path


class FoodPieChartMixin(BasePieChartMixin):
    food = None
    images_directory = f"food"

    def sizes(self):
        return self.food.get_percents_form_macros()


class DiaryCaloriesPieChartMixin(BasePieChartMixin):
    diary = None
    images_directory = f"diary_calories"

    def sizes(self):
        return self.diary.get_meals_calories_percents()


class DiaryMacrosPieChartMixin(BasePieChartMixin):
    diary = None
    images_directory = f"diary_macros"

    def sizes(self):
        return self.diary.get_meals_macros_percents()


class BaseOpenFoodRepoMixin:
    NUTRIENTS_NAMES_MAPPER = {
        "energy_kcal": "energy",
        "fat": "fat",
        "fatty_acids_total_saturated": "saturated_fat",
        "monounsaturated_fatty_acids": "monounsaturated_fat",
        "polyunsaturated_fatty_acids": "polyunsaturated_fat",
        "fatty_acids_total_trans": "trans_fat",
        "cholesterol": "cholesterol",
        "carbohydrates": "carbs",
        "sugars": "sugars",
        "fiber": "fiber",
        "protein": "protein",
        "iron": "iron",
        "calcium": "calcium",
        "sodium": "sodium",
        "vitamin_c_ascorbic_acid": "vitamin_c",
        "vitamin_a_iu": "vitamin_a",
    }

    KEY = os.environ.get("OPEN_FOOD_REPO_API_KEY")
    BASE_URL = "https://www.foodrepo.org/api/v3"
    ENDPOINT = ""
    HEADERS = {
        'Authorization': 'Token token=' + KEY,
        'Accept': 'application/json',
        'Content-Type': 'application/vnd.api+json',
        'Accept-Encoding': 'gzip,deflate'
    }

    @property
    def url(self):
        return f"{self.BASE_URL}{self.ENDPOINT}"

    def _clean_food_data(self, food_data: dict) -> dict:
        name = food_data.get("display_name_translations")
        ingredients = food_data.get("ingredients_translations")
        nutrients = food_data.get("nutrients") or {}

        food_cleaned_data = {
            "name": name.get("en") if name is not None else "" or "",
            "ingredients": ingredients.get("en") if ingredients is not None else "" or "",
        }

        for key, value in nutrients.items():
            if key in self.NUTRIENTS_NAMES_MAPPER:
                food_cleaned_data[self.NUTRIENTS_NAMES_MAPPER[key]] = value.get("per_hundred") \
                    if value is not None else 0 or 0

        return food_cleaned_data


class SearchOpenFoodMixin(BaseOpenFoodRepoMixin):
    ENDPOINT = "/products/_search"
    SEARCH_QUERY = {
        "from": 0,
        "size": 10000,
        "query": {
            "wildcard": {
                "_all_names": "",
            },
        },
    }
    ACCURATE_SEARCH_QUERY = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {}
                    }
                ],
            },
        },
    }

    def get_food_by_searched_string(self, searched_string: str, accurate_search=False) -> list:
        data = {}
        query = self.__get_query(searched_string, accurate_search)
        response = requests.post(self.url, json=query, headers=self.HEADERS)
        if response.status_code == 200:
            data = self.__get_searched_data(response.json())
        return self.__clean_searched_data(**data)

    def __get_query(self, searched_string: str, accurate_search: bool) -> dict:
        if accurate_search:
            query = self.ACCURATE_SEARCH_QUERY.copy()
            query["query"]["bool"]["must"][0]["match"]["name_translations.en"] = f"{searched_string.lower()}"
        else:
            query = self.SEARCH_QUERY.copy()
            query["query"]["wildcard"]["_all_names"] = f"*{searched_string.lower()}*"
        return query

    def __get_searched_data(self, results) -> dict:
        data = {}

        for hit in results["hits"]["hits"]:
            food_cleaned_data = self._clean_food_data(hit["_source"])
            if self.__is_food_valid(food_cleaned_data):
                name = food_cleaned_data.get("name")
                data[name] = {
                    "energy": food_cleaned_data.get("energy"),
                    "fat": food_cleaned_data.get("fat"),
                    "carbs": food_cleaned_data.get("carbs"),
                    "protein": food_cleaned_data.get("protein"),
                    "food_id": hit["_source"].get("id"),
                }

        return data

    @staticmethod
    def __clean_searched_data(**data) -> list:
        cleaned_data = []

        for name, nutrients in sorted(data.items(), key=lambda kvp: kvp[0]):
            cleaned_data.append((name, [kvp for kvp in nutrients.items()]))

        return cleaned_data

    @staticmethod
    def __is_food_valid(food_data: dict) -> bool:
        name = food_data.get("name")
        energy = food_data.get("energy") or 0
        protein = food_data.get("protein") or 0
        carbs = food_data.get("carbs") or 0
        fat = food_data.get("fat") or 0

        required_macros = (
            protein > 0,
            carbs > 0,
            fat > 0,
        )

        if name and len(name) < 100 and energy > 0 and any(required_macros):
            return True
        return False


class GetOpenFoodMixin(BaseOpenFoodRepoMixin):
    ENDPOINT = "/products"

    def get_food_by_id(self, food_id: int) -> dict:
        url = f"{self.url}/{food_id}"
        response = requests.get(url, headers=self.HEADERS)
        if response.status_code == 200:
            food_data = response.json().get("data")
            return self._clean_food_data(food_data)
