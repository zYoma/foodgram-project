# Generated by Django 3.1.1 on 2020-09-02 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_auto_20200902_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Слаг'),
        ),
    ]