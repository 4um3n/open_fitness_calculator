import os
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_delete, pre_save
from open_fitness_calculator.diary.models import Diary
from open_fitness_calculator.profiles.models import MacrosPercents, Goal, Profile, DailyNutrients


@receiver(pre_save, sender=Profile)
def delete_profile_picture_pre_save(sender, instance, *args, **kwargs):
    try:
        profile = sender.objects.get(pk=instance.pk)
        old_picture_path = profile.profile_picture.path
        if old_picture_path.split(os.sep)[-2] != "default" and old_picture_path != instance.profile_picture.path:
            profile.profile_picture.delete(save=False)
    except ObjectDoesNotExist:
        pass


@receiver(post_save, sender=Profile)
def post_save_profile(sender, instance, *args, **kwargs):
    if not Goal.objects.filter(profile=instance).exists():
        Goal.objects.create(profile=instance).save()

    if not MacrosPercents.objects.filter(profile=instance).exists():
        MacrosPercents.objects.create(profile=instance).save()

    if not Diary.objects.filter(profile=instance, is_completed=False).exists():
        Diary.objects.create(profile=instance).save()

    try:
        daily_nutrients = DailyNutrients.objects.get(profile=instance)
    except ObjectDoesNotExist:
        daily_nutrients = DailyNutrients.objects.create(profile=instance)

    daily_nutrients.set_daily_nutrients()
    daily_nutrients.save()


@receiver(pre_delete, sender=Profile)
def delete_profile_picture_pre_delete_profile(sender, instance, *args, **kwargs):
    for food in instance.food_set.all():
        if not food.is_admin:
            food.delete()

    for exercise in instance.exercise_set.all():
        if not exercise.is_admin:
            exercise.delete()

    if instance.profile_picture.path.split(os.sep)[-2] != "default":
        instance.profile_picture.delete(save=False)


@receiver(post_save, sender=MacrosPercents)
def update_daily_nutrients_macros(sender, instance, *args, **kwargs):
    profile = instance.profile

    if DailyNutrients.objects.filter(profile=profile).exists():
        profile.dailynutrients.set_daily_nutrients()
        profile.dailynutrients.save()
