from django.apps import AppConfig


class FoodConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'open_fitness_calculator.food'

    def ready(self):
        from open_fitness_calculator.food import signals
