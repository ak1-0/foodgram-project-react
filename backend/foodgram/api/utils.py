from io import BytesIO
from reportlab.lib.pagesizes import letter
from django.http import FileResponse, HttpResponse
from reportlab.platypus import Paragraph, SimpleDocTemplate
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import status
from recipes.models import Recipe
from rest_framework.response import Response
from django.db.models import F

from recipes.models import RecipeIngredientAmount
from users.models import Subscription
from .recipe_service import RecipeService
from .constants import NUMBERING


def shop_list(request):
    file_format = request.GET.get('format', 'txt')

    ingredients = RecipeIngredientAmount.objects.filter(
        recipe__in_shopping_carts__user=request.user).values(
        'ingredient__name',
        'ingredient__measurement_unit').annotate(
        ingredient_name=F('ingredient__name'),
        total_amount=Sum('amount'))
    ingredients.values_list('ingredient__name',
                            'ingredient__measurement_unit',
                            'total_amount')
    shopping_cart = 'Что купить:\n'

    index = NUMBERING
    for ingredient in ingredients:
        name = ingredient['ingredient_name'].capitalize()
        measure = ingredient['ingredient__measurement_unit']
        total_amount = ingredient['total_amount']
        shopping_cart += f'{index}. {name}: {total_amount} {measure}\n'
        index += NUMBERING

    if file_format.lower() == 'pdf':
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        elements = []
        shopping_cart_lines = shopping_cart.split('\n')
        for line in shopping_cart_lines:
            elements.append(Paragraph(line, encoding='utf-8'))

        doc.build(elements)

        buffer.seek(0)
        response = FileResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.pdf"'
        )
        return response
    else:
        response = HttpResponse(shopping_cart,
                                content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response


def is_user_subscribed(request, obj):
    """
    Проверка подписки пользователя на объект.
    """
    return (
        request.user.is_authenticated
        and Subscription.objects.filter(user=request.user, author=obj).exists()
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
