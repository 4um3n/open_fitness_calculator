from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from open_fitness_calculator.diary.models import Diary
from open_fitness_calculator.diary.signals import create_not_completed_diary
from open_fitness_calculator.fitness_calculator_auth.models import FitnessCalculatorUser
from open_fitness_calculator.profiles.models import Profile


@receiver(post_save, sender=FitnessCalculatorUser)
def create_profile(sender, instance, *args, **kwargs):
    """ Create Profile on FitnessCalculatorUser creation """
    if not Profile.objects.filter(user=instance).exists():
        kwargs = {"user": instance}

        if instance.is_staff:
            kwargs.update({
                "is_staff": True,
            })
        elif instance.is_superuser:
            kwargs.update({
                "is_admin": True,
            })

        Profile.objects.create(**kwargs).save()


@receiver(pre_delete, sender=FitnessCalculatorUser)
def disconnect_create_not_completed_diary_if_not_exist(sender, instance, *args, **kwargs):
    post_delete.disconnect(
        sender=Diary,
        receiver=create_not_completed_diary,
    )


@receiver(post_delete, sender=FitnessCalculatorUser)
def connect_create_not_completed_diary_if_not_exist(sender, instance, *args, **kwargs):
    post_delete.connect(
        sender=Diary,
        receiver=create_not_completed_diary,
    )
