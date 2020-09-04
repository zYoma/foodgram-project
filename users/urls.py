from django.contrib.auth import views
from django.urls import path
from .forms import EmailValidationOnForgotPassword
from .views import register, Follows, Favorites, Shopping, get_shop_list


urlpatterns = [
    path('login/', views.LoginView.as_view(template_name='users/authForm.html',), name='login'),
    path('logout/', views.LogoutView.as_view(template_name='users/logged_out.html',), name='logout'),
    path('password-reset/', views.PasswordResetView.as_view(
        form_class=EmailValidationOnForgotPassword,
        template_name='users/resetPassword.html'), name='password_reset'),
    path('password-reset/done/', views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path('register/', register, name="register"),
    path('password-change/', views.PasswordChangeView.as_view(template_name='users/changePassword.html',
        success_url="/"), name='password_change'),
    path('password-change/done/', views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    path('follows/', Follows.as_view(), name='follows_url'),
    path('favorites/<int:id>/', Favorites.as_view(), name='del_favorites_url'),
    path('favorites/', Favorites.as_view(), name='favorites_url'),
    path('purchases/<int:id>/', Shopping.as_view(), name='del_shopping_url'),
    path('purchases/', Shopping.as_view(), name='shopping_url'),
    path('get-shop-list/', get_shop_list, name='shop_list_url'),
]