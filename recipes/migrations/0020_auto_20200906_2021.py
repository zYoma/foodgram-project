# Generated by Django 3.1.1 on 2020-09-06 17:21
import csv
from django.db import migrations
from django.db import IntegrityError
from django.db import transaction


def upload_ingedients(apps, schema_editor):
    """ Заливаем данные из файла ingredients.csv в Таблицу Ingredient
        Делим строку по символу ','. Присваиваем сзначения полям таблицы
        name и units соответственно.Если после запятой пустая строка - ставим 'г'.Можете поменять это поведение.
        Загружаем все данные в одном запросе методом bulk_create.
    """
    csv_file='ingredients.csv'
    Ingredient = apps.get_model('recipes', 'Ingredient')
    data = csv.reader(open(csv_file, encoding='utf-8'), delimiter = ',')
    try:
        obj_list = [
            Ingredient( 
                id = id,
                name = row[0],
                units = 'г' if row[1] == '' else row[1],
            )
            for id, row in enumerate(data)
        ]
    except IndexError:
        return 'IndexError'
    
    try:
        with transaction.atomic():
            Ingredient.objects.bulk_create(obj_list)
    except IntegrityError:
        return 'Ингридиенты уже в БД!'

    return 'ok'


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0019_auto_20200906_2019'),
    ]

    operations = [
        migrations.RunPython(upload_ingedients)
    ]
