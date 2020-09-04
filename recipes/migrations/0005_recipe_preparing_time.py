# Generated by Django 3.1.1 on 2020-09-02 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_remove_recipe_preparing_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='preparing_time',
            field=models.IntegerField(default=10, verbose_name='Время приготовления(мин.)'),
            preserve_default=False,
        ),
    ]
