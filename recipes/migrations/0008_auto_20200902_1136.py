# Generated by Django 3.1.1 on 2020-09-02 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20200902_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='units',
            field=models.CharField(max_length=15, verbose_name='Единицы измерения'),
        ),
    ]
