from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete, post_delete

from open_fitness_calculator.food.models import Food, DiaryFood, FoodPieChart


@receiver(post_save, sender=Food)
def food_post_save__create_food_pie_chart(sender, instance, *args, **kwargs):
    if not hasattr(instance, "foodpiechart"):
        FoodPieChart.objects.create(food=instance).save()

    instance.foodpiechart.reset_pie_chart()


@receiver(post_save, sender=Food)
def food_post_save__reset_diary_pie_charts(sender, instance, *args, **kwargs):
    for diary_food in instance.diaryfood_set.all():
        diary_food.diary.caloriespiechart.reset_pie_chart()
        diary_food.diary.macrospiechart.reset_pie_chart()


@receiver(pre_delete, sender=Food)
def food_pre_delete__delete_foodpiechart_image(sender, instance, *args, **kwargs):
    if hasattr(instance, "foodpiechart"):
        instance.foodpiechart.delete_cloudinary_pie_chart()


@receiver(post_save, sender=DiaryFood)
def diary_food_post_save__reset_diary_pie_charts(sender, instance, *args, **kwargs):
    instance.diary.caloriespiechart.reset_pie_chart()
    instance.diary.macrospiechart.reset_pie_chart()


@receiver(post_delete, sender=DiaryFood)
def diary_food_post_delete__reset_diary_pie_charts(sender, instance, *args, **kwargs):
    instance.diary.caloriespiechart.reset_pie_chart()
    instance.diary.macrospiechart.reset_pie_chart()
