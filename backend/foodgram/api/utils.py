from io import BytesIO

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph

from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe, RecipeIngredientAmount
from users.models import Subscription
from .constants import NUMBERING, START
from .recipe_service import RecipeService


def download_shopping_cart(request):
    ingredients = RecipeIngredientAmount.objects.filter(
        recipe__in_shopping_carts__user=request.user).values(
        'ingredient__name',
        'ingredient__measurement_unit').annotate(
        total_amount=Sum('amount'))
    data = ingredients.values_list('ingredient__name',
                                   'ingredient__measurement_unit',
                                   'total_amount')
    shopping_cart = 'Что купить:\n'

    NUMBERING = 1
    for name, measure, amount in data:
        name = name.capitalize()
        shopping_cart += f'{NUMBERING}. {name} - {amount} {measure}\n'
        NUMBERING += 1

    # Создание PDF-документа
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Загрузка шрифта Arial
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

    # Создание стиля для абзаца с использованием шрифта Arial
    styles = getSampleStyleSheet()
    para_style = styles['Normal']
    para_style.fontName = 'Arial'

    # Создание элементов документа (абзацев)
    elements = []
    shopping_cart_lines = shopping_cart.split('\n')
    for line in shopping_cart_lines:
        elements.append(Paragraph(line, para_style))

    # Сборка документа
    doc.build(elements)

    # Подготовка и отправка HTTP-ответа с PDF-файлом
    buffer.seek(START)
    response = FileResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="shopping_cart.pdf"'
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
