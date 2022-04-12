from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from open_fitness_calculator.diary.models import Diary
from open_fitness_calculator.diary.signals import diary_post_delete__create_not_completed_diary
from open_fitness_calculator.fitness_calculator_auth.models import FitnessCalculatorUser
from open_fitness_calculator.profiles.models import Profile


@receiver(post_save, sender=FitnessCalculatorUser)
def user_post_save__create_profile(sender, instance, *args, **kwargs):
    if not Profile.objects.filter(user=instance).exists():
        kwargs = {"user": instance}

        if instance.is_staff:
            kwargs.update({"is_staff": True})
        elif instance.is_superuser:
            kwargs.update({"is_admin": True})

        Profile.objects.create(**kwargs).save()


@receiver(pre_delete, sender=FitnessCalculatorUser)
def user_pre_delete__disconnect_signals(sender, instance, *args, **kwargs):
    post_delete.disconnect(
        sender=Diary,
        receiver=diary_post_delete__create_not_completed_diary,
    )


@receiver(post_delete, sender=FitnessCalculatorUser)
def user_post_delete__connect_disconnected_signals(sender, instance, *args, **kwargs):
    post_delete.connect(
        sender=Diary,
        receiver=diary_post_delete__create_not_completed_diary,
    )
