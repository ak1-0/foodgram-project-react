from django.contrib import admin

from .models import Recipe, Ingredient, Tag, ShoppingCart, Favorite


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    verbose_name='Рецепт',
    list_display = ('id', 'name', 'author', 'count_favorites')
    list_filter = ('author', 'name', 'tags',)

    @staticmethod
    def count_favorites(obj):
        return obj.in_favorites.count()
    count_favorites.short_description='Количество в избранном'


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

admin.site.site_header = 'Панель администратора FoodGram'
admin.site.index_title = 'Рецепты и пользователи'
