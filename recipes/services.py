import json

from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Ingredient, IngredientQuantity


def assembly_ingredients(ingredients_names, ingredients_values):
    """ Функция получает два списка (список имен ингридиентов и их колличеством),
        создает объекты в таблице IngredientQuantity если таких нет,
        и возвращает список всех созданных объектов.
    """
    ingredients_list = []
    for n, name in enumerate(ingredients_names):
        try:
           ingredient = Ingredient.objects.get(name=name)
        except Ingredient.DoesNotExist:
            return []
        ingr_quan, created = IngredientQuantity.objects.get_or_create(
            defaults={
                'ingredient': ingredient,
                'quantity': ingredients_values[n],
            },
            ingredient=ingredient,
            quantity=ingredients_values[n]
        )
        ingredients_list.append(ingr_quan)

    return ingredients_list


def get_paginator(request, objs):
    """ Пагинатор для использования в различных представлениях. """
    get_copy = request.GET.copy()
    parameters = get_copy.pop('page', True) and get_copy.urlencode()
    paginator = Paginator(objs, 6)
    last_page = paginator.num_pages
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    is_paginator = page.has_other_pages()
    if page.has_previous():
        prev_url = '?page={}'.format(page.previous_page_number())
    else:
        prev_url = ''

    if page.has_next():
        next_url = '?page={}'.format(page.next_page_number())
    else:
        next_url = ''

    return is_paginator, prev_url, next_url, parameters, last_page, page


def get_id_recipe(request):
    """ Функция получает id рецепта из тела запроса. """
    body = json.loads(request.body)
    return  body.get('id')


def change_ingredients(ingredients_list, ingredients, recipe):
    """ Функция меняет список ингридиентов рецепта, если он был изменен. """
    if ingredients_list != list(ingredients) and ingredients_list:
        ingredients.delete()
        recipe.ingredients.add(*ingredients_list)


def get_author(request, author):
    """ Функция возвращает автора для создания объекта подписки """
    if author is None:
        recipe_id = get_id_recipe(request)
        author = get_object_or_404(Recipe.objects.select_related('author'), id=recipe_id).author
    else:
        author = get_object_or_404(User, username=author)

    return author
