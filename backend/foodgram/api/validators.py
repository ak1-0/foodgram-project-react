from rest_framework import serializers


def validate_username_format(value):
    """
    Проверка корректности имени пользователя.
    """
    allowed_characters = (
        'abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        '0123456789.@+-_'
    )
    for char in value:
        if char not in allowed_characters:
            raise serializers.ValidationError(
                "Username should only contain letters, digits, "
                "and @/./+/-/_ characters."
            )
    return value


def validate_ingredient_amount(value):
    """
    Проверка корректности количества ингредиента.
    """
    for ingredient in value:
        amount = ingredient.get('amount')
        if amount == 0:
            raise serializers.ValidationError('Количество ингредиента должно быть больше нуля!')
    return value


def validate_cooking_duration(value):
    """
    Проверка корректности времени приготовления.
    """
    if value < 1:
        raise serializers.ValidationError('Время приготовления должно быть не менее 1 минуты')
    

def validate_updated_password(value, initial_data):
    """
    Проверка корректности нового пароля.
    """
    if value == initial_data.get('current_password'):
        raise serializers.ValidationError('Новый пароль не может совпадать со старым')
    return value
