from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500
from .views import page_not_found
from .views import server_error
from .views import redirect_recipes


handler404 = "foodgram.views.page_not_found"
handler500 = "foodgram.views.server_error"

urlpatterns = [
    path("404/", page_not_found),
    path("500/", server_error),
    path('admin/', admin.site.urls),
    path('user/',  include('users.urls')),
    path('recipes/',  include('recipes.urls')),
    path('', redirect_recipes),

]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
