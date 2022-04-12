import os
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete, post_delete, pre_save
from open_fitness_calculator.food.models import Food, DiaryFood, FoodPieChart


@receiver(pre_save, sender=Food)
def food_pre_save__set_food_pie_chart(sender, instance, *args, **kwargs):
    if sender.objects.filter(pk=instance.pk).exists():
        instance.foodpiechart.create_pie_chart()
        file_path = instance.foodpiechart.get_file_path()
        FoodPieChart.objects.filter(pk=instance.foodpiechart.pk).update(image=file_path)


@receiver(post_save, sender=Food)
def food_post_save__create_food_pie_chart(sender, instance, *args, **kwargs):
    if not hasattr(instance, "foodpiechart"):
        food_pie_chart = FoodPieChart.objects.create(food=instance)
        food_pie_chart.save()
        instance.save()


@receiver(pre_delete, sender=Food)
def food_pre_delete__delete_food_pie_chart_image(sender, instance, *args, **kwargs):
    if instance.foodpiechart.image.path.split(os.sep)[-2] != "default":
        instance.foodpiechart.image.delete(save=False)


@receiver(post_save, sender=DiaryFood)
def diary_food_pre_save__recreate_and_set_diary_pie_chart(sender, instance, *args, **kwargs):
    instance.diary.save()


@receiver(post_delete, sender=DiaryFood)
def diary_food_post_delete__recreate_and_set_diary_pie_chart(sender, instance, *args, **kwargs):
    instance.diary.save()

