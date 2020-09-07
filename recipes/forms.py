from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Recipe


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = ('name', 'tag', 'preparing_time', 'description', 'image')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form__input', 'id': 'id_name'}),
            'tag': forms.CheckboxSelectMultiple(),
            'preparing_time': forms.NumberInput(attrs={'class': 'form__input', 'id': 'id_time'}),
            'description': forms.Textarea(attrs={'class': 'form__textarea', 'id': 'id_description', 'rows': '8'}),
        }
        labels = {
            'name': _('Название рецепта'),
            'preparing_time': _('Время приготовления'),
            'description': _('Описание'),
            'image': _('Загрузить фото'),
        }
