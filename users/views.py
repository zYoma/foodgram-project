from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from .forms import UserRegistrationForm
from recipes.models import Recipe, Subscription, Favorite, ShoppingList
from recipes.services import get_paginator, ObjectMixin
import json


def register(request):
    '''Представление формы регистрации пользователя'''
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            email = user_form.cleaned_data['email']
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            new_user.refresh_from_db()

            return render(request, 'users/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()

    return render(request, 'users/reg.html', {
        'user_form': user_form,
    })


class Follows(LoginRequiredMixin, View):
    '''Представление страницы Мои подписки'''
    login_url = '/user/login/'

    def get(self, request):
        follows = Subscription.objects.select_related('author', 'user').filter(user=request.user)
        
        return render(request, 'users/myFollow.html', context={'follows': follows })


class Favorites(LoginRequiredMixin, ObjectMixin, View):
    '''Представление страницы Избранное'''
    login_url = '/user/login/'
    model = Favorite


class Shopping(ObjectMixin, View):
    '''Представление страницы Список покупок'''
    model = ShoppingList

    def get(self, request):
        '''Если пользователь не авторизирован, используем сессии'''
        if request.user.is_authenticated:
            recipes = Recipe.objects.filter(shopping_list__user=request.user)
        else:
            buying_list = request.session.get('shopping_list', [])
            recipes = Recipe.objects.filter(id__in=buying_list)
        return render(request, 'users/shopList.html', {'recipes': recipes})


def get_shop_list(request):
    '''Функция возвращает файл со списком ингридиентов'''
    result = create_shopping_list(request)
    filename = "ingredients.txt"
    response = HttpResponse(result, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response


def create_shopping_list(request):
    '''Алгоритм формирования списка ингридиентов для покупки.
       Складывает значения одинаковых ингредиентов и формирует читабельный список.
    '''
    if request.user.is_authenticated:
        recipes = Recipe.objects.filter(shopping_list__user=request.user)
    else:
        buying_list = request.session.get('shopping_list', [])
        recipes = Recipe.objects.filter(id__in=buying_list)
    ingredients = []
    for recipe in recipes:
        inng_list = recipe.ingredients.all()
        for i in inng_list:
            new = i.create_shopping_list()
            ingredients.append(new)

    result = {}
    for i in ingredients:
        if not i[0] in result:
            result[i[0]] = i[1]
        else:
            result[i[0]] += i[1]

    content = []
    for key, value in result.items():
        for i in ingredients:
            if i[0] == key:
                ing = f'{key} - {value} {i[2]}\n'
                content.append(ing)
                break

    return content
