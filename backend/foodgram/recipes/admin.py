from django.contrib import admin
from django.db.models import Count

from .models import (Favorite, Ingredient, Recipe,
                     ShoppingCart, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'count_favorites')
    list_filter = ('author', 'name', 'tags',)

    @staticmethod
    def count_favorites(obj):
        return obj.count_favorites.aggregate(count=Count('id'))['count']
    count_favorites.short_description = 'Количество в избранных'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass
