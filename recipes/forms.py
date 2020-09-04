from django import forms
from .models import Recipe
from django.utils.translation import ugettext_lazy


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = ('name', 'tag', 'preparing_time', 'description', 'image')
        widgets = {
            'name':forms.TextInput(attrs={'class': 'form__input', 'id': 'id_name'}),
            'tag':forms.CheckboxSelectMultiple(),
            'preparing_time':forms.NumberInput(attrs={'class': 'form__input', 'id': 'id_time'}),
            'description':forms.Textarea(attrs={'class': 'form__textarea', 'id': 'id_description', 'rows': '8'}),
        }
        labels = {
            'name': ugettext_lazy('Название рецепта'),
            'preparing_time': ugettext_lazy('Время приготовления'),
            'description': ugettext_lazy('Описание'),
            'image': ugettext_lazy('Загрузить фото'),
        }