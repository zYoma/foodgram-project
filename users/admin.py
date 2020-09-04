from django.contrib import admin
from django.contrib.auth.models import User


class UserAdmin(admin.ModelAdmin):
    list_filter = ("email", "username" )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
