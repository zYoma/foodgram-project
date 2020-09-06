from django.contrib import admin
from .models import Ingredient, IngredientQuantity, Recipe
from .models import Subscription, Favorite, ShoppingList


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'units')
    search_fields = ('name',)
    list_filter = ('name', )


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_author')
    search_fields = ('name', 'get_author')
    list_filter = ('author__username', 'name', 'tag')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')

    def get_author(self, obj):
        return obj.author.username


class IngredientQuantityAdmin(admin.ModelAdmin):
    list_display = ('get_ingredient', 'quantity')
    search_fields = ('get_ingredient',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ingredient')

    def get_units(self, obj):
        return obj.ingredient.units

    def get_ingredient(self, obj):
        return obj.ingredient.name


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'get_author')
    search_fields = ('get_user',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'author')

    def get_user(self, obj):
        return obj.user.username

    def get_author(self, obj):
        return obj.author.username


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'get_recipe')
    search_fields = ('get_user',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'recipe')

    def get_user(self, obj):
        return obj.user.username

    def get_recipe(self, obj):
        return obj.recipe.name


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'get_recipe')
    search_fields = ('get_user',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'recipe')

    def get_user(self, obj):
        return obj.user.username

    def get_recipe(self, obj):
        return obj.recipe.name


admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(IngredientQuantity, IngredientQuantityAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
