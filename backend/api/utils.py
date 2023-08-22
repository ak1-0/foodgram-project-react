from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe
from users.models import Subscription
from .recipe_service import RecipeService


def is_user_subscribed(request, obj):
    """
    Проверка подписки пользователя на объект.
    """
    return (
        request.user.is_authenticated
        and Subscription.objects.filter(user=request.user,
                                        author=obj).exists()
    )


def recipe_add_or_del(request, model, pk, custom_serializer):
    """
    Добавление или удаление рецепта из модели связей с пользователем.
    """
    recipe = get_object_or_404(Recipe, id=pk)
    if request.method == 'POST':
        added = RecipeService.add(request, recipe, model)
        if added:
            serializer = custom_serializer(recipe)
            status_code = status.HTTP_201_CREATED
            response_data = {
                'detail': f'Рецепт добавлен в {model.__name__}!',
                'data': serializer.data
            }
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                'message': f'Рецепт уже добавлен в {model.__name__}'
            }
    else:
        removed = RecipeService.remove(request, recipe, model)
        if removed:
            status_code = status.HTTP_204_NO_CONTENT
            response_data = {
                'detail': f'Рецепт удален из {model.__name__}'
            }
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                'message': f'Рецепт не найден в {model.__name__}'
            }

    return Response(response_data, status=status_code)
