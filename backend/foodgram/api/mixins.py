from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, status

from recipes.models import (Favorite,
                            Recipe,
                            ShoppingCart
                            )
from users.models import Subscription, User
from .serializers import (BriefRecipeSerializer,
                          ChangePasswordSerializer,
                          RecipeFollowSerializer,
                          UserFollowSerializer
                          )
from .utils import recipe_add_or_del


class BaseRecipeMixin:
    """
    Миксин для работы с рецептами.
    """
    def get_recipe(self, pk):
        """
        Получить рецепт по его ID.
        """
        try:
            return Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            raise Http404

    def add_to_favorites(self, request, pk):
        """
        Добавить рецепт в избранное.
        """
        recipe = self.get_recipe(pk)
        Favorite.objects.create(user=request.user, recipe=recipe)
        return Response({'detail': 'Рецепт добавлен в избранное'})

    def _remove_from_favorites(self, request, pk):
        """
        Удалить рецепт из избранного.
        """
        recipe = self.get_recipe(pk)
        favorite = Favorite.objects.filter(user=request.user,
                                           recipe=recipe).first()
        if favorite:
            favorite.delete()
            return Response({'detail': 'Рецепт удален из избранного'})
        else:
            return Response({'detail': 'Рецепт не найден в избранном'},
                            status=status.HTTP_404_NOT_FOUND)

    def favorite_recipe(self, request, pk):
        """
        Добавить/удалить рецепт в/из избранного.
        """
        return recipe_add_or_del(request=request,
                                 model=Favorite,
                                 pk=pk,
                                 custom_serializer=BriefRecipeSerializer)

    def _add_to_shopping_cart(self, request, pk):
        """
        Добавить рецепт в корзину.
        """
        recipe = self.get_recipe(pk)
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        return Response({'detail': 'Рецепт добавлен в корзину'})

    def _remove_from_shopping_cart(self, request, pk):
        """
        Удалить рецепт из корзины.
        """
        recipe = self.get_recipe(pk)
        shopping_cart = ShoppingCart.objects.filter(user=request.user,
                                                    recipe=recipe).first()
        if shopping_cart:
            shopping_cart.delete()
            return Response({'detail': 'Рецепт удален из корзины'})
        else:
            return Response({'detail': 'Рецепт не найден в корзине'},
                            status=status.HTTP_404_NOT_FOUND)


class SubscriptionsMixin:
    """
    Миксин для работы с подписками: получение подписок пользователя.
    """
    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        """
        Получить список подписок пользователя.
        """
        queryset = User.objects.filter(subscriber__user=self.request.user)
        pages = self.paginate_queryset(queryset)
        serializer = UserFollowSerializer(pages,
                                          many=True,
                                          context={'request': request})
        return self.get_paginated_response(serializer.data)


class SubscribeMixin:
    """
    Миксин для работы с подписками: подписка и отписка от авторов.
    """
    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        """
        Подписаться или отписаться от автора.
        """
        author = get_object_or_404(User,
                                   id=kwargs['id'])

        if request.method == 'POST':
            serializer = RecipeFollowSerializer(author,
                                                data=request.data,
                                                context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=request.user,
                                        author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        get_object_or_404(Subscription,
                          user=request.user,
                          author=author).delete()
        return Response({'detail': 'Вы отписались от автора'},
                        status=status.HTTP_204_NO_CONTENT)


class SetPasswordMixin(object):
    """
    Миксин для установки нового пароля текущего пользователя.
    """
    @action(detail=False, methods=['POST'],
            permission_classes=(permissions.IsAuthenticated,))
    def set_password(self, request):
        """Установить новый пароль для текущего пользователя."""
        serializer = ChangePasswordSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteRecipeMixin(BaseRecipeMixin):
    """
    Миксин для добавления и удаления рецептов из избранного пользователя.
    """
    @action(detail=True, methods=['GET', 'POST', 'DELETE'],
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        """
        Получить, добавить или удалить рецепт из избранного.
        """
        if request.method == 'GET':
            return self._get_favorite(request, pk)
        elif request.method == 'POST':
            return self.add_to_favorites(request, pk)
        elif request.method == 'DELETE':
            return self._remove_from_favorites(request, pk)


class ShoppingCartMixin(BaseRecipeMixin):
    """
    Миксин для функциональности корзины покупок.
    """

    @action(detail=True, methods=['POST', 'DELETE'])
    def shopping_cart(self, request, pk):
        """
        Добавить или удалить рецепт из корзины покупок.
        """
        if request.method == 'POST':
            return self._add_to_shopping_cart(request, pk)
        elif request.method == 'DELETE':
            return self._remove_from_shopping_cart(request, pk)
