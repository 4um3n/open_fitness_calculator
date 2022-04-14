# Generated by Django 4.0 on 2022-04-14 19:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '0001_initial'),
        ('exercises', '0001_initial'),
        ('diary', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercise',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.profile'),
        ),
        migrations.AddField(
            model_name='diaryexercise',
            name='diary',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diary.diary'),
        ),
        migrations.AddField(
            model_name='diaryexercise',
            name='exercise',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exercises.exercise'),
        ),
    ]
