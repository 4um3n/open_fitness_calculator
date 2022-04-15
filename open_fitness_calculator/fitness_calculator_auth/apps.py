from django.apps import AppConfig


class FitnessCalculatorAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'open_fitness_calculator.fitness_calculator_auth'

    def ready(self):
        from open_fitness_calculator.fitness_calculator_auth import signals
