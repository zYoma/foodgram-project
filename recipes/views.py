from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.db.models import F, Q
from django.contrib.auth.models import User
from .forms import RecipeForm
from .services import assembly_ingredients, get_paginator, ObjectMixin
from .models import Ingredient, Ingredient_quantity, Recipe
from .models import Subscription, Favorite, ShoppingList
import json


class Index(ObjectMixin, View):
    pass


class Author(ObjectMixin, View):
    pass


class SinglePage(View):
    '''Представление для отдельной страницы рецепта.'''
    def get(self, request, slug):
        subsc = False
        fav = False
        recipe = get_object_or_404(Recipe.objects.select_related('author'), slug=slug)
        if request.user.is_authenticated:
            subsc = Subscription.objects.filter(user=request.user, author=recipe.author).exists()
            fav = Favorite.objects.filter(user=request.user, recipe=recipe).exists()
            buying = ShoppingList.objects.filter(user=request.user, recipe=recipe).exists()
        else:
            buying = request.session.get('shopping_list', [])
            buying = True if recipe.id in buying else False

        return render(request, 'recipes/singlePage.html', context={
            'recipe': recipe,
            'subsc': subsc,
            'fav': fav,
            'buying': buying,
        })


class Find_Ingredients(View):
    '''Поиск ингридиентов при вводе в input на странице
       добавления рецепта. Возвращает json c результатами поиска.
    '''
    def get(self, request):
        q = request.GET.get('query', '')
        results = list(Ingredient.objects.filter(name__istartswith=q)
            .annotate(title=F('name'), dimension=F('units')).values('title', 'dimension'))
        return JsonResponse(results, safe=False, json_dumps_params={'ensure_ascii': False})


class AddRecipe(LoginRequiredMixin, View):
    '''Представление формы добавления рецепта'''
    login_url = '/user/login/'

    def get(self, request):
        form = RecipeForm()
        return render(request, 'recipes/recipe_form.html', context={'form': form})

    def post(self, request):
        form = RecipeForm(request.POST, request.FILES)
        ingredients_names = request.POST.getlist('nameIngredient')
        ingredients_values = request.POST.getlist('valueIngredient')
        ingredients_list = assembly_ingredients(ingredients_names, ingredients_values)
        if ingredients_list == []:
            return render(request, 'recipes/recipe_form.html', context={'form': form, 'error': True})

        if form.is_valid():
            new_recipe = form.save(commit=False)
            new_recipe.author = request.user
            new_recipe.save()
            new_recipe.ingredients.add(*ingredients_list)
        else:
            return render(request, 'recipes/recipe_form.html', context={'form': form})

        return redirect(reverse('single_page_url',  kwargs={'slug': new_recipe.slug}))


class EditRecipe(LoginRequiredMixin, View):
    '''Представление формы редактирования рецепта'''
    login_url = '/user/login/'

    def get(self, request, slug):
        recipe = get_object_or_404(Recipe, slug=slug)
        if request.user != recipe.author:
            return redirect(reverse('single_page_url',  kwargs={'slug': recipe.slug}))

        form = RecipeForm(instance=recipe)
        return render(request, 'recipes/recipe_form.html', context={'form': form, 'recipe': recipe})

    def post(self, request, slug):
        recipe = get_object_or_404(Recipe, slug=slug)
        if request.user != recipe.author:
            return redirect(reverse('single_page_url',  kwargs={'slug': recipe.slug}))

        ingredients = recipe.ingredients.all()
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        ingredients_names = request.POST.getlist('nameIngredient')
        ingredients_values = request.POST.getlist('valueIngredient')
        ingredients_list = assembly_ingredients(ingredients_names, ingredients_values)
       
        if form.is_valid():
            form.save()
            if ingredients_list != list(ingredients) and ingredients_list != []:
                ingredients.delete()
                recipe.ingredients.add(*ingredients_list)
        else:
            return render(request, 'recipes/recipe_form.html', context={'form': form, 'recipe': recipe})

        return redirect(reverse('single_page_url',  kwargs={'slug': recipe.slug}))


class DeleteRecipe(LoginRequiredMixin, View):
    '''Удаление рецепта'''
    login_url = '/user/login/'

    def post(self, request, slug):
        recipe = get_object_or_404(Recipe, slug=slug)
        if request.user != recipe.author:
            return redirect(reverse('single_page_url',  kwargs={'slug': recipe.slug}))

        recipe.delete()
        return redirect(reverse('index_url'))


class Subscriptions(LoginRequiredMixin, View):
    login_url = '/user/login/'

    def get(self, request):
        '''Так как специалисты по фронтенду сделали на разных страницах
           обсолютно по разному обработку одного и тогоже действия
           пришлось немного закостылить, чтобы не повторяться.
        '''
        author = request.GET.get('author')
        if 'sub' in request.GET:
            get_object_or_404(Subscription.objects.select_related('author'),
                user=request.user, author__username=author).delete()

        else:
            self.post(request, author)
        return redirect(reverse('author_url',  kwargs={'username': author}))

    def post(self, request, author=None):
        '''Создание подписки на автора если ее еще нет.'''
        if author is None:
            body = json.loads(request.body)
            recipe_id = body.get('id')
            author = get_object_or_404(Recipe.objects.select_related('author'), id=recipe_id).author
        else:
            author = get_object_or_404(User, username=author)

        user = request.user
        subs, created = Subscription.objects.get_or_create(
            defaults={
                'user': user,
                'author': author,
            },
            user=user,
            author=author,
        )
        if created:
            results = {"success": True}
        else:
            results = {"success": False}
        return JsonResponse(results, safe=False, json_dumps_params={'ensure_ascii': False})


    def delete(self, request, id):
        '''Удаляем подписку если она существует'''
        author = get_object_or_404(Recipe.objects.select_related('author'), id=id).author
        try:
            subs = Subscription.objects.get(user=request.user, author=author)
        except Subscription.DoesNotExist:
            results = {"success": False}
        else:
            subs.delete()
            results = {"success": True}

        return JsonResponse(results, safe=False, json_dumps_params={'ensure_ascii': False})
