from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete

from open_fitness_calculator.food.models import DiaryFood
from open_fitness_calculator.diary.models import Diary, CaloriesPieChart, MacrosPieChart
from open_fitness_calculator.fitness_calculator_auth.models import FitnessCalculatorUser
from open_fitness_calculator.food.signals import diary_food_post_delete__reset_diary_pie_charts


@receiver(post_save, sender=Diary)
def diary_post_save__reset_pie_charts(sender, instance, *args, **kwargs):
    if not hasattr(instance, "caloriespiechart"):
        CaloriesPieChart.objects.create(diary=instance).save()

    if not hasattr(instance, "macrospiechart"):
        MacrosPieChart.objects.create(diary=instance).save()

    instance.caloriespiechart.reset_pie_chart()
    instance.macrospiechart.reset_pie_chart()


@receiver(post_save, sender=Diary)
def diary_post_save__create_new_not_completed_diary(sender, instance, *args, **kwargs):
    not_completed_diary_exists = sender.objects.filter(
        profile=instance.profile,
        is_completed=False,
    ).exists()

    if instance.is_completed and not not_completed_diary_exists:
        sender.objects.create(profile=instance.profile).save()


@receiver(pre_delete, sender=Diary)
def diary_pre_delete__delete_pie_charts_images(sender, instance, *args, **kwargs):
    instance.caloriespiechart.delete_cloudinary_pie_chart()
    instance.macrospiechart.delete_cloudinary_pie_chart()


@receiver(pre_delete, sender=Diary)
def diary_pre_delete__disconnect_signals(sender, instance, *args, **kwargs):
    post_delete.disconnect(
        sender=DiaryFood,
        receiver=diary_food_post_delete__reset_diary_pie_charts,
    )


@receiver(post_delete, sender=Diary)
def diary_post_delete__connect_signals(sender, instance, *args, **kwargs):
    post_delete.connect(
        sender=DiaryFood,
        receiver=diary_food_post_delete__reset_diary_pie_charts
    )


@receiver(post_delete, sender=Diary)
def diary_post_delete__create_not_completed_diary(sender, instance, *args, **kwargs):
    """
    Create new Diary if not completed Diary
    was deleted and Profile.user exists
    """
    diary_exist = sender.objects.filter(profile=instance.profile, is_completed=False).exists()
    user_exists = FitnessCalculatorUser.objects.filter(pk=instance.profile.pk).exists()

    if not diary_exist and user_exists:
        sender.objects.create(profile=instance.profile).save()
