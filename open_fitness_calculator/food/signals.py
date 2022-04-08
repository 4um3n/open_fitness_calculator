import os
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete, post_delete, pre_save
from open_fitness_calculator.food.models import Food, DiaryFood, FoodPieChart


@receiver(pre_save, sender=Food)
def set_food_pie_chart(sender, instance, *args, **kwargs):
    if sender.objects.filter(pk=instance.pk).exists():
        instance.foodpiechart.create_pie_chart()
        file_path = instance.foodpiechart.get_file_path()
        FoodPieChart.objects.filter(pk=instance.foodpiechart.pk).update(image=file_path)


@receiver(post_save, sender=Food)
def create_food_pie_chart(sender, instance, *args, **kwargs):
    if not hasattr(instance, "foodpiechart"):
        food_pie_chart = FoodPieChart.objects.create(food=instance)
        food_pie_chart.save()
        instance.save()


@receiver(pre_delete, sender=Food)
def delete_food_pie_chart(sender, instance, *args, **kwargs):
    """
    Clean deleted Food old pie chart png file
    """
    if instance.foodpiechart.image.path.split(os.sep)[-2] != "default":
        instance.foodpiechart.image.delete(save=False)


@receiver(post_save, sender=DiaryFood)
def change_diary_pie_chart_post_save_meal(sender, instance, *args, **kwargs):
    instance.diary.save()


@receiver(post_delete, sender=DiaryFood)
def change_diary_pie_chart_post_delete_meal(sender, instance, *args, **kwargs):
    instance.diary.save()

