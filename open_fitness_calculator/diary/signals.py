import os
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete

from open_fitness_calculator.food.models import DiaryFood
from open_fitness_calculator.diary.models import Diary, CaloriesPieChart, MacrosPieChart
from open_fitness_calculator.fitness_calculator_auth.models import FitnessCalculatorUser
from open_fitness_calculator.food.signals import diary_food_post_delete__recreate_and_set_diary_pie_chart


@receiver(pre_save, sender=Diary)
def diary_pre_save__create_pie_charts(sender, instance, *args, **kwargs):
    if sender.objects.filter(pk=instance.pk).exists():
        instance.caloriespiechart.create_pie_chart()
        instance.macrospiechart.create_pie_chart()


@receiver(post_save, sender=Diary)
def diary_post_save__create_and_set_pie_charts(sender, instance, *args, **kwargs):
    profile = instance.profile

    if not hasattr(instance, "caloriespiechart"):
        calories_pie_chart = CaloriesPieChart.objects.create(diary=instance)
        calories_pie_chart.save()

    if not hasattr(instance, "macrospiechart"):
        macros_pie_chart = MacrosPieChart.objects.create(diary=instance)
        macros_pie_chart.save()

    if instance.is_completed and not sender.objects.filter(profile=instance.profile, is_completed=False).exists():
        sender.objects.create(profile=profile).save()

    CaloriesPieChart.objects.filter(pk=instance.caloriespiechart.pk).update(
        image=instance.caloriespiechart.get_file_path()
    )

    MacrosPieChart.objects.filter(pk=instance.macrospiechart.pk).update(
        image=instance.macrospiechart.get_file_path()
    )


@receiver(pre_delete, sender=Diary)
def diary_pre_delete__delete_pie_charts_images(sender, instance, *args, **kwargs):
    if instance.caloriespiechart.image.path.split(os.sep)[-2] != "default":
        instance.caloriespiechart.image.delete(save=False)

    if instance.macrospiechart.image.path.split(os.sep)[-2] != "default":
        instance.macrospiechart.image.delete(save=False)


@receiver(pre_delete, sender=Diary)
def diary_pre_delete__disconnect_signals(sender, instance, *args, **kwargs):
    post_delete.disconnect(
        sender=DiaryFood,
        receiver=diary_food_post_delete__recreate_and_set_diary_pie_chart,
    )


@receiver(post_delete, sender=Diary)
def diary_post_delete__connect_signals(sender, instance, *args, **kwargs):
    post_delete.connect(
        sender=DiaryFood,
        receiver=diary_food_post_delete__recreate_and_set_diary_pie_chart
    )


@receiver(post_delete, sender=Diary)
def diary_post_delete__create_not_completed_diary(sender, instance, *args, **kwargs):
    """
    Create new Diary if not completed Diary was deleted and Profile.user exists
    """
    diary_exist = sender.objects.filter(profile=instance.profile, is_completed=False).exists()
    user_exists = FitnessCalculatorUser.objects.filter(pk=instance.profile.pk).exists()

    if not diary_exist and user_exists:
        sender.objects.create(profile=instance.profile).save()
