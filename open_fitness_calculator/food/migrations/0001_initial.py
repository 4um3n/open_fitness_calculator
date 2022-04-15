# Generated by Django 4.0 on 2022-04-15 12:32

import cloudinary.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import open_fitness_calculator.core.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '0001_initial'),
        ('diary', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('ingredients', models.CharField(blank=True, default='', max_length=500)),
                ('is_admin', models.BooleanField(default=False)),
                ('energy', models.IntegerField(default=0)),
                ('protein', models.FloatField(default=0)),
                ('carbs', models.FloatField(default=0)),
                ('fiber', models.FloatField(default=0)),
                ('sugars', models.FloatField(default=0)),
                ('fat', models.FloatField(default=0)),
                ('saturated_fat', models.FloatField(default=0)),
                ('polyunsaturated_fat', models.FloatField(default=0)),
                ('monounsaturated_fat', models.FloatField(default=0)),
                ('trans_fat', models.FloatField(default=0)),
                ('cholesterol', models.FloatField(default=0)),
                ('sodium', models.FloatField(default=0)),
                ('potassium', models.FloatField(default=0)),
                ('calcium', models.FloatField(default=0)),
                ('iron', models.FloatField(default=0)),
                ('vitamin_a', models.FloatField(default=0)),
                ('vitamin_c', models.FloatField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Food',
            },
            bases=(models.Model, open_fitness_calculator.core.mixins.FoodMacrosConvertorMixin),
        ),
        migrations.CreateModel(
            name='FoodCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('red_meat', 'Red Meat'), ('white_meat', 'White Meat'), ('fruits', 'Fish'), ('red_meat', 'Root Vegetables'), ('green_leafy_vegetables', 'Green Leafy Vegetables'), ('fruits', 'Fruits'), ('berries', 'Berries')], max_length=25)),
            ],
            options={
                'verbose_name_plural': 'Food Categories',
            },
        ),
        migrations.CreateModel(
            name='FoodPieChart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', cloudinary.models.CloudinaryField(max_length=255, verbose_name='Image')),
                ('food', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='food.food')),
            ],
            bases=(models.Model, open_fitness_calculator.core.mixins.BaseFoodPieChartMixin),
        ),
        migrations.AddField(
            model_name='food',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='food.foodcategory'),
        ),
        migrations.AddField(
            model_name='food',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.profile'),
        ),
        migrations.CreateModel(
            name='DiaryFood',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meal_type', models.CharField(choices=[('Breakfast', 'Breakfast'), ('Lunch', 'Lunch'), ('Dinner', 'Dinner'), ('Snack', 'Snack')], max_length=9)),
                ('quantity', models.FloatField(default=100, validators=[django.core.validators.MinValueValidator(0)])),
                ('diary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diary.diary')),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='food.food')),
            ],
        ),
    ]
