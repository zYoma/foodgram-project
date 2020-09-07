from django.urls import path

from .views import (
	AddRecipe,
	FindIngredients,
	Index,
    SinglePage,
    EditRecipe,
    Author,
    Subscriptions,
    DeleteRecipe,
)


urlpatterns = [
    path('add/', AddRecipe.as_view(), name='add_recipes_url'),
    path('ingredients/', FindIngredients.as_view(), name='find_ingredients_url'),
    path('', Index.as_view(), name='index_url'),
    path('edit/<str:slug>/', EditRecipe.as_view(), name='edit_recipes_url'),
    path('delete/<str:slug>/', DeleteRecipe.as_view(), name='delete_recipes_url'),
    path('author/<str:username>/', Author.as_view(), name='author_url'),
    path('subscriptions/<int:id>/', Subscriptions.as_view(), name='del_subscriptions_url'),
    path('subscriptions/', Subscriptions.as_view(), name='add_subscriptions_url'),
    path('<str:slug>/', SinglePage.as_view(), name='single_page_url'),
]