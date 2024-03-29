# Generated by Django 4.0 on 2022-04-15 12:32

import cloudinary.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import open_fitness_calculator.core.mixins
import open_fitness_calculator.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('fitness_calculator_auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('is_admin', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('requested_staff', models.BooleanField(default=False)),
                ('first_name', models.CharField(blank=True, max_length=30, validators=[open_fitness_calculator.core.validators.validate_username_isalnum])),
                ('last_name', models.CharField(blank=True, max_length=30, validators=[open_fitness_calculator.core.validators.validate_username_isalnum])),
                ('age', models.IntegerField(default=14, validators=[django.core.validators.MinValueValidator(14), django.core.validators.MaxValueValidator(150)])),
                ('weight', models.FloatField(default=50, validators=[django.core.validators.MinValueValidator(30), django.core.validators.MaxValueValidator(500)])),
                ('height', models.FloatField(default=165, validators=[django.core.validators.MinValueValidator(100), django.core.validators.MaxValueValidator(250)])),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female')], default='male', max_length=6)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='fitness_calculator_auth.fitnesscalculatoruser')),
                ('profile_picture', cloudinary.models.CloudinaryField(max_length=255, verbose_name='Image')),
            ],
        ),
        migrations.CreateModel(
            name='DailyNutrients',
            fields=[
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='profiles.profile')),
                ('daily_calories', models.FloatField(default=0)),
                ('daily_protein', models.FloatField(default=0)),
                ('daily_carbs', models.FloatField(default=0)),
                ('daily_fiber', models.FloatField(default=0)),
                ('daily_sugars', models.FloatField(default=0)),
                ('daily_fat', models.FloatField(default=0)),
                ('daily_saturated_fat', models.FloatField(default=0)),
                ('daily_monounsaturated_fat', models.FloatField(default=0)),
                ('daily_polyunsaturated_fat', models.FloatField(default=0)),
                ('daily_trans_fat', models.FloatField(default=0)),
                ('daily_cholesterol', models.FloatField(default=300)),
                ('daily_sodium', models.FloatField(default=2300)),
                ('daily_potassium', models.FloatField(default=3500)),
                ('daily_vitamin_a', models.FloatField(default=100)),
                ('daily_vitamin_c', models.FloatField(default=100)),
                ('daily_calcium', models.FloatField(default=100)),
                ('daily_iron', models.FloatField(default=100)),
            ],
            options={
                'verbose_name_plural': 'Daily nutrients',
            },
            bases=(models.Model, open_fitness_calculator.core.mixins.DailyCaloriesCalculatorMixin),
        ),
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='profiles.profile')),
                ('goal', models.CharField(choices=[('loose', 'Loose'), ('maintain', 'Maintain'), ('gain', 'Gain')], default='maintain', max_length=10)),
                ('activity_level', models.CharField(choices=[('not_active', 'Low'), ('low', 'Light'), ('medium', 'Medium'), ('high', 'High')], default='medium', max_length=10)),
                ('per_week', models.PositiveIntegerField(choices=[(150, '150g'), (250, '250g'), (500, '500g'), (750, '750g'), (1000, '1000g')], default=500)),
            ],
        ),
        migrations.CreateModel(
            name='MacrosPercents',
            fields=[
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='profiles.profile')),
                ('protein', models.PositiveIntegerField(default=20, validators=[django.core.validators.MaxValueValidator(100)])),
                ('carbs', models.PositiveIntegerField(default=50, validators=[django.core.validators.MaxValueValidator(100)])),
                ('fat', models.PositiveIntegerField(default=30, validators=[django.core.validators.MaxValueValidator(100)])),
            ],
            options={
                'verbose_name_plural': 'Macros Percents',
            },
        ),
    ]
