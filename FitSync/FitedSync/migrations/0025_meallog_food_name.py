# Generated by Django 5.1 on 2024-11-19 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FitedSync', '0024_rename_carbs_meallog_carbohydrates'),
    ]

    operations = [
        migrations.AddField(
            model_name='meallog',
            name='food_name',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
    ]
