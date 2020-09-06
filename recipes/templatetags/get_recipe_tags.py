from django import template
from django.shortcuts import get_object_or_404
from recipes.models import Recipe

register = template.Library()

@register.filter 
def get_recipe_tags(recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    tags_list = recipe.tag
    tags = ''
    if 'lunch' in tags_list:
        tags += str('<li class="card__item"><span class="badge badge_style_green">Обед</span></li>')
    if 'breakfast' in tags_list:
        tags += str('<li class="card__item"><span class="badge badge_style_orange">Завтрак</span></li>')
    if 'dinner' in tags_list:
        tags += str('<li class="card__item"><span class="badge badge_style_purple">Ужин</span></li>')

    return tags