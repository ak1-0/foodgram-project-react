from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'email',)
    list_filter = ('email', 'first_name',)


admin.site.register(Subscription)