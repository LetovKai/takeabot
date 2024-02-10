from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'api_key', 'sellers_id')

admin.site.register(User, UserAdmin)