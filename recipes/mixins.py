from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .models import Recipe, Subscription, Favorite, ShoppingList
from .services import get_paginator, get_id_recipe


class IndexPageMixin:
    """ Класс миксин. Для того, чтобы не копипастить одни и теже методы
        в нескольких предтсавлениях.
    """
    model = None

    def get(self, request, username=None):
        """ Представление для главной страницы, страницы автора, избранного.
            Помимо самих рецептов, возвращает переменные для проверки состояния переключателей.
            subsc - подписан на автора или нет. fav_list - список с id рецептов которые в избранном.
            buying_list - список с id рецептов, добавленных в покупки. Пагинатор.
            Также, фильтрация по тегам при наличии get параметра tag.
        """
        subsc = get_subscription(request, username)
        buying_list = get_buying_list(request)
        fav_list = get_fav_list(request)
        recipes = get_recipes(request, username, fav_list)
        tag_list = []
        if 'tag' in request.GET:
            tag_list, recipes = formation_tags(request, recipes)       

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
        """ Общий метод для добавления в список покупок, избранное.
            Для неавторизированных пользователей на основе сессий.
        """
        recipe_id = get_id_recipe(request)
        if request.user.is_authenticated:    
            results = create_buy_or_fav(request, recipe_id, model=self.model)
        else:
            results = create_buy_or_fav_for_guest(request, recipe_id)

        return JsonResponse(results, safe=False, json_dumps_params={'ensure_ascii': False})


    def delete(self, request, id):
        """ Общий метод для удаления из список покупок, избранного, подписок.
            Для неавторизированных пользователей на основе сессий.
        """
        if request.user.is_authenticated:
            results = delete_buy_or_fav(request, id, model=self.model)
        else:
            results = delete_buy_or_fav_for_guest(request, id)

        return JsonResponse(results, safe=False, json_dumps_params={'ensure_ascii': False})


def formation_tags(request, recipes):
    """ Формируем список рецептов в зависимости от выбранных тегов. """
    tag = request.GET.get('tag')
    tag_list = tag.split('__')        
    or_condition = Q()
    for i in tag_list:
        or_condition.add(Q(tag__contains=i), Q.OR)

    return tag_list, recipes.filter(or_condition)


def get_subscription(request, username):
    """ Функция возвращает True если пользователь подписан на автора. """
    subsc = False
    if username is not None and request.user.is_authenticated:
        subsc = Subscription.objects.select_related('author').filter(
            user=request.user, author__username=username).exists()

    return subsc


def get_buying_list(request):
    """ Функция возвращает список покупок пользователя. """
    if request.user.is_authenticated:
        buying_list = ShoppingList.objects.select_related('recipe').filter(
                user=request.user).values_list('recipe__id', flat=True)
    else:
        buying_list = request.session.get('shopping_list', [])

    return buying_list


def get_fav_list(request):
    """ Функция возвращает список id избранных рецептов. """
    fav_list = []
    if request.user.is_authenticated:       
        fav_list = Favorite.objects.select_related('recipe').filter(
            user=request.user).values_list('recipe__id', flat=True)

    return fav_list
        

def get_recipes(request, username, fav_list):
    """ Функция возвращает список рецептов в зависимости от того, с какой страницы был запрос. """
    if username is None:
        if request.path == reverse('favorites_url'):
            recipes = Recipe.objects.select_related('author').filter(id__in=fav_list)
        else:
            recipes = Recipe.objects.select_related('author').all()
    else:
        recipes = Recipe.objects.select_related('author').filter(author__username=username)

    return recipes


def create_buy_or_fav(request, recipe_id, model):
    """ Функция создает объекты списка покупок и избранного для автоизированного пользователя. """
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user
    obj, created = model.objects.get_or_create(
        defaults={
            'user': user,
            'recipe': recipe,
        },
        user=user,
        recipe=recipe,
    )

    return {'success': bool(created)}


def create_buy_or_fav_for_guest(request, recipe_id):
    """ Функция создает объекты списка покупок и избранного для гостей (сессии). """
    if 'shopping_list' in request.session:
        shopping_list = request.session['shopping_list']
        recipe_id = int(recipe_id)
        if not recipe_id in shopping_list:
            shopping_list.append(recipe_id)
            request.session['shopping_list'] =shopping_list
    else:
        request.session['shopping_list'] = [recipe_id]

    return {'success': True}


def delete_buy_or_fav(request, id, model):
    """ Функция удаляет объект из списка покупок или избранного у авторизированного поьзователя. """
    recipe = get_object_or_404(Recipe, id=id)
    try:
        obj = model.objects.get(user=request.user, recipe=recipe)
    except Subscription.DoesNotExist:
        results = {'success': False}
    else:
        obj.delete()
        results = {'success': True}

    return results


def delete_buy_or_fav_for_guest(request, id):
    """ Функция удаляет объект из списка покупок или избранного у гостей (сессиии). """
    shopping_list = request.session.get('shopping_list')
    try:
       shopping_list.remove(int(id))
    except ValueError:
        results = {'success': False}
    else:
        request.session['shopping_list'] = shopping_list
        results = {'success': True}

    return results