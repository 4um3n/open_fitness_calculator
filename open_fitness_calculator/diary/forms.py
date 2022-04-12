from open_fitness_calculator.diary.models import Diary
from open_fitness_calculator.core.forms import FitnessCalculatorModelForm


class DiaryForm(FitnessCalculatorModelForm):
    class_name = f"form-control diary"
    placeholders = {"name": "Name"}
    widgets_attrs = {
        "is_completed": {
            "hidden": "hidden",
        },
        "end_date": {
            "hidden": "hidden",
        },
    }

    class Meta:
        model = Diary
        fields = ("name", "is_completed", "end_date",)
