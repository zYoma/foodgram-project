import os

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from multiselectfield import MultiSelectField
from pytils.translit import slugify


TAGS = (
    ('breakfast', 'завтрак'),
    ('lunch', 'обед'),
    ('dinner', 'ужин'),
)


class Ingredient(models.Model):
    name =  models.CharField(max_length=100, verbose_name=_('Название'))    
    units = models.CharField(max_length=15, verbose_name=_('Единицы измерения'))

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'units'], name='unique_ingredient'),
        ]
        verbose_name = 'Ингридиент'
        verbose_name_plural = "Ингридиенты"
        ordering = ['name']


class IngredientQuantity(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
        related_name='ingredient_quantitys', verbose_name=_('Ингридиент'))
    quantity = models.IntegerField(verbose_name=_('Колличество'))

    def __str__(self):
        return f'{self.ingredient.name} - {self.quantity} {self.ingredient.units}'

    def create_shopping_list(self):
        return self.ingredient.name, self.quantity, self.ingredient.units


    class Meta:
        verbose_name = 'Ингридиент для рецепты'
        verbose_name_plural = 'Ингридиенты для рецепта'


class Recipe(models.Model):
    def validate_image(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        kilobyte_limit = settings.RECIPE_IMAGE_LIMIT
        if filesize > kilobyte_limit * 1024:
            raise ValidationError(
                'Максимальный размер изображения %s Kbyte' % str(kilobyte_limit))

    def file_name(instance, filename):
        ext = filename.split('.')[-1]
        filename = f'{instance.slug}.{ext}'
        fullname = os.path.join(settings.MEDIA_ROOT, 'images/', filename)
        if os.path.exists(fullname):
            os.remove(fullname)

        return f'images/{filename}'

    author = models.ForeignKey(User, on_delete=models.CASCADE,
        related_name='recipes', verbose_name=_('Автор'))
    name =  models.CharField(max_length=100, verbose_name=_('Название'))
    image = models.ImageField(upload_to=file_name, validators=[validate_image],
        verbose_name=_('Картинка'))
    description = models.TextField(verbose_name=_('Текстовое описание'))
    tag = MultiSelectField(choices=TAGS, verbose_name=_('Тег'))
    ingredients = models.ManyToManyField(IngredientQuantity, related_name='recipes',
        verbose_name=_('Ингридиенты'))
    preparing_time = models.IntegerField(verbose_name=_('Время приготовления(мин.)'))
    pub_date = models.DateTimeField(auto_now=True, verbose_name=_('Дата добавления'))
    slug = models.SlugField(editable=False, unique = True, verbose_name=_('Слаг'))

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions',
        verbose_name=_('Пользователь'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_subscriptions',
        verbose_name=_('Автор'))

    def get_recipes(self):
        return Recipe.objects.select_related('author').filter(author__username=self.author)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], name='unique_subscription'),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
        related_name='favorites', verbose_name=_('Пользователь'))
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
        related_name='favorites', verbose_name=_('Рецепт'))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'], name='unique_favorite'),
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
        related_name='shopping_lists', verbose_name=_('Пользователь'))
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
        related_name='shopping_lists', verbose_name=_('Рецепт'))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'], name='unique_shopping_list'),
        ]
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
