from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import F, Q
from .models import Ingredient, Ingredient_quantity
from .models import Recipe, Subscription, Favorite, ShoppingList
import json


class ObjectMixin():
    '''Класс миксин. Для того, чтобы не копипастить одни и теже методы
       в нескольких предтсавлениях
    '''
    model = None

    def get(self, request, username=None):
        '''Представление для главной страницы, страницы автора, избранного.
           Помимо самих рецептов, возвращает переменные для проверки состояния переключателей.
           subsc - подписан на автора или нет. fav_list - список с id рецептов которые в избранном.
           buying_list - список с id рецептов, добавленных в покупки. Пагинатор.
           Также, фильтрация по тегам при наличии get параметра tag.
        '''
        subsc = False
        if request.user.is_authenticated:       
            fav_list = Favorite.objects.select_related('recipe').filter(
                user=request.user).values_list('recipe__id', flat=True)
            buying_list = ShoppingList.objects.select_related('recipe').filter(
                user=request.user).values_list('recipe__id', flat=True)
        else:
            fav_list = []
            buying_list = request.session.get('shopping_list', [])
            
        if username is None:
            if request.path == '/user/favorites/':
                recipes = Recipe.objects.select_related('author').filter(id__in=fav_list)
            else:
                recipes = Recipe.objects.select_related('author').all()
        else:
            recipes = Recipe.objects.select_related('author').filter(author__username=username)
            if request.user.is_authenticated:
                subsc = Subscription.objects.select_related('author').filter(
                    user=request.user, author__username=username).exists()

        tag_list = []

        if 'tag' in request.GET:
            tag = request.GET.get('tag')
            tag_list = tag.split('__')
            if len(tag_list) == 3:
                recipes = recipes.filter(Q(tag__contains='breakfast') | Q(tag__contains='lunch') | Q(tag__contains='dinner'))
            elif len(tag_list) == 2:
                recipes = recipes.filter(Q(tag__contains=tag_list[0]) | Q(tag__contains=tag_list[1]))
            elif len(tag_list) == 1:
                recipes = recipes.filter(Q(tag__contains=tag_list[0]))

        is_paginator, prev_url, next_url, parameters, last_page, page = get_paginator(request, recipes)

        return render(request, 'recipes/index.html', context={
            'recipes': page,
            'is_paginator': is_paginator,
            'prev_url': prev_url,
            'next_url': next_url,
            'parameters': parameters,
            'page_end': last_page,
            'tag_list': tag_list,
            'author': username,
            'subsc': subsc,
            'fav_list': fav_list,
            'buying_list': buying_list,

        })


    def post(self, request):
        '''Общий метод для добавления в список покупок, избранное, подписки.
           Для неавторизированных пользователей на основе сессий.
        '''
        body = json.loads(request.body)
        recipe_id = body.get('id')
        if request.user.is_authenticated:    
            recipe = get_object_or_404(Recipe, id=recipe_id)
            user = request.user
            obj, created = self.model.objects.get_or_create(
                defaults={
                    'user': user,
                    'recipe': recipe,

                },
                user=user,
                recipe=recipe,
            )
            if created:
                results = {"success": True}
            else:
                results = {"success": False}
        
        else:
            if 'shopping_list' in request.session:
                 shopping_list = request.session['shopping_list']
                 if not int(recipe_id) in shopping_list:
                    shopping_list.append(int(recipe_id))
                    request.session['shopping_list'] = shopping_list
            else:
                request.session['shopping_list'] = [int(recipe_id)]

            results = {"success": True}

        return JsonResponse(results, safe=False, json_dumps_params={'ensure_ascii': False})


    def delete(self, request, id):
        '''Общий метод для удаления из список покупок, избранного, подписок.
           Для неавторизированных пользователей на основе сессий.
        '''
        if request.user.is_authenticated:
            recipe = get_object_or_404(Recipe, id=id)
            try:
                obj = self.model.objects.get(user=request.user, recipe=recipe)
            except Subscription.DoesNotExist:
                results = {"success": False}
            else:
                obj.delete()
                results = {"success": True}

        else:
            shopping_list = request.session.get('shopping_list')
            try:
               shopping_list.remove(int(id))
            except ValueError:
                results = {"success": False}
            else:
                request.session['shopping_list'] = shopping_list
                results = {"success": True}

        return JsonResponse(results, safe=False, json_dumps_params={'ensure_ascii': False})



def assembly_ingredients(ingredients_names, ingredients_values):
    '''Функция получает два списка (список имен ингридиентов и их колличеством),
       создает объекты в таблице Ingredient_quantity если таких нет,
       и возвращает список всех созданных объектов.
    '''
    ingredients_list = []
    for n, name in enumerate(ingredients_names):
        try:
           ingredient = Ingredient.objects.get(name=name)
        except Ingredient.DoesNotExist:
            return []
        ingr_quan, created = Ingredient_quantity.objects.get_or_create(
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
    '''Пагинатор для использования в различных представлениях'''
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
