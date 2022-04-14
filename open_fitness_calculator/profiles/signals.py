import os.path
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_delete, pre_save

from open_fitness_calculator.settings import BASE_DIR
from open_fitness_calculator.diary.models import Diary
from open_fitness_calculator.profiles.models import MacrosPercents, Goal, Profile, DailyNutrients


@receiver(pre_save, sender=Profile)
def profile_pre_save__upload_default_profile_picture(sender, instance, *args, **kwargs):
    if not sender.objects.filter(pk=instance.pk).exists():
        profile_picture_path = os.path.join(BASE_DIR, "media", "images", "profile_pictures", "default", "default.png")
        instance.profile_picture = instance.upload_new_profile_picture(profile_picture_path)


@receiver(post_save, sender=Profile)
def profile_post_save(sender, instance, *args, **kwargs):
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
def profile_pre_delete__delete_non_admin_food_and_exercises(sender, instance, *args, **kwargs):
    for food in instance.food_set.all():
        if not food.is_admin:
            food.delete()

    for exercise in instance.exercise_set.all():
        if not exercise.is_admin:
            exercise.delete()


@receiver(pre_delete, sender=Profile)
def profile_pre_delete__delete_profile_picture(sender, instance, *args, **kwargs):
    instance.delete_profile_picture()


@receiver(post_save, sender=MacrosPercents)
def macros_percents__update_daily_nutrients_macros(sender, instance, *args, **kwargs):
    profile = instance.profile

    if DailyNutrients.objects.filter(profile=profile).exists():
        profile.dailynutrients.set_daily_nutrients()
        profile.dailynutrients.save()
