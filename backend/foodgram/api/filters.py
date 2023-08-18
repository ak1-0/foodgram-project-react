from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class RecipeSearchFilter(FilterSet):
    """
    Фильтр рецептов на основе автора,
    тегов, статуса добавленных в избранное и наличия в корзине покупок.
    """
    author = filters.NumberFilter(field_name='author__id')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
                                        method='filter_is_favorited'
                                        )
    is_in_shopping_cart = filters.BooleanFilter(
                                        method='filter_is_in_shopping_cart'
                                        )

    def filter_is_favorited(self, queryset, name, value):
        """
        Фильтрует рецепты по статусу добавленных в избранное.
        """
        if value and not self.request.user.is_anonymous:
            return self._filter_by_favorited(queryset)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """
        Фильтрует рецепты по статусу наличия в корзине покупок.
        """
        if value and not self.request.user.is_anonymous:
            return self._filter_by_in_shopping_cart(queryset)
        return queryset

    def _filter_by_favorited(self, queryset):
        """
        Фильтрует рецепты по статусу добавленных в избранное
        (внутренний метод).
        """
        return queryset.filter(in_favorites__user=self.request.user)

    def _filter_by_in_shopping_cart(self, queryset):
        """
        Фильтрует рецепты по статусу наличия в корзине покупок
        (внутренний метод).
        """
        return queryset.filter(in_shopping_carts__user=self.request.user)

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')


class IngredientSearchFilter(SearchFilter):
    """Фильтр ингредиентов по названию."""
    search_param = 'name'
