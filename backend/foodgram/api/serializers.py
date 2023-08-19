from django.db import transaction
from rest_framework import serializers

from djoser.serializers import UserCreateSerializer, UserSerializer

from recipes.models import (Favorite,
                            Ingredient,
                            Recipe,
                            RecipeIngredientAmount,
                            ShoppingCart,
                            Tag)
from users.models import User
from .fields import Base64ImageField
from .utils import is_user_subscribed
from .validators import (validate_username_format,
                         validate_ingredient_amount,
                         validate_cooking_duration,
                         validate_updated_password)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = 'id', 'name', 'measurement_unit'


class CreateIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления ингредиентов при создании рецепта.
    """
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredientAmount
        fields = 'id', 'amount'


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тегов.
    """

    class Meta:
        model = Tag
        fields = 'id', 'name', 'color', 'slug'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения ингридиентов в рецепте.
    """
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredientAmount
        fields = ['id', 'name', 'measurement_unit', 'amount']

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class SubscribedMixin:
    """
    Миксин для проверки подписки пользователя.
    """

    def get_is_subscribed(self, obj):
        return is_user_subscribed(request=self.context.get('request'), obj=obj)


class UsersSerializer(SubscribedMixin, UserSerializer):
    """
    Сериализатор пользователей.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed')


class CreateUserSerializer(SubscribedMixin, UserCreateSerializer):
    """
    Сериализатор для создания пользователей.
    """
    username = serializers.CharField(max_length=150,
                                     validators=[validate_username_format])

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password', 'id')


class FullRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецептов.
    """
    author = UsersSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipes')
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        """
        Возвращает, добавлен ли рецепт в избранное у текущего пользователя.
        """
        return (self.context.get('request')
                and not self.context.get('request').user.is_anonymous
                and self.context.get('request').user.favorites.filter(
                    recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        """
        Возвращает, добавлен ли рецепт в корзину покупок
        текущего пользователя.
        """
        return (self.context.get('request')
                and not self.context.get('request').user.is_anonymous
                and self.context.get('request').user.shopping_carts.filter(
                    recipe=obj).exists())

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'name', 'image', 'text',
                  'ingredients', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания рецептов.
    """
    ingredients = CreateIngredientSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)
    author = UsersSerializer(read_only=True)

    def validate(self, attrs):
        """
        Проверяет валидность данных перед созданием рецепта.
        """
        validated_attrs = super().validate(attrs)
        validate_ingredient_amount(validated_attrs.get('ingredients'))
        validate_cooking_duration(validated_attrs.get('cooking_time'))
        return validated_attrs

    class Meta:
        model = Recipe
        fields = '__all__'

    @staticmethod
    def save_ingredients(recipe, ingredient_data_list):
        """
        Сохраняет связи между рецептом и ингредиентами с их количеством.
        """
        recipe_ingredient_amounts = [
            RecipeIngredientAmount(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient['amount']
            )
            for ingredient in ingredient_data_list
        ]
        with transaction.atomic():
            RecipeIngredientAmount.objects.filter(recipe=recipe).delete()
            RecipeIngredientAmount.objects.bulk_create(
                recipe_ingredient_amounts)

    def create(self, validated_data):
        """
        Создает новый рецепт с установленными ингредиентами и автором.
        """
        ingredient_data_list = validated_data.pop('ingredients')
        tag_data_list = validated_data.pop('tags')
        author = self.context['request'].user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tag_data_list)
        self.save_ingredients(recipe, ingredient_data_list)
        return recipe

    def update(self, instance, validated_data):
        """
        Обновляет данные рецепта и связи
        с ингредиентами при обновлении рецепта.
        """
        if 'ingredients' in validated_data:
            ingredient_data_list = validated_data.pop('ingredients')
            RecipeIngredientAmount.objects.filter(recipe=instance).delete()
            RecipeIngredientAmount.objects.bulk_create([
                RecipeIngredientAmount(
                    recipe=instance,
                    ingredient_id=ingredient.get('id'),
                    amount=ingredient['amount']
                )
                for ingredient in ingredient_data_list
            ])
        if 'tags' in validated_data:
            instance.tags.set(validated_data['tags'])
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """
        Преобразует объект рецепта в сериализованный вид.
        """
        context = {'request': self.context.get('request')}
        return FullRecipeSerializer(instance, context=context).data


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для рецептов."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'


class BriefRecipeSerializer(BaseRecipeSerializer):
    """Сокращенный сериализатор для рецептов."""
    pass


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного (добавление и удаление рецептов)."""

    recipe = BriefRecipeSerializer()

    class Meta:
        model = Favorite
        fields = 'user', 'recipe'


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок (добавление и удаление)."""

    recipe = BriefRecipeSerializer()

    class Meta:
        model = ShoppingCart
        fields = 'user', 'recipe'


class ChangePasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для изменения пароля пользователя."""
    old_password = serializers.CharField()
    new_password = serializers.CharField(
        validators=[validate_updated_password])

    class Meta:
        model = User
        fields = ['old_password', 'new_password']


class BaseUserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для пользователей."""
    email = serializers.EmailField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)

    def get_recipes(self, obj):
        """
        Возвращает список рецептов пользователя
        с ограничением по количеству.
        """
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = BriefRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    @staticmethod
    def get_recipes_count(obj):
        """
        Возвращает общее количество рецептов у пользователя.
        """
        return obj.recipes.count()

    class Meta:
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name']


class RecipeFollowSerializer(BaseUserSerializer, UsersSerializer):
    """
    Сериализатор для подписки пользователя.
    """
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = BaseUserSerializer.Meta.fields + ['recipes_count',
                                                   'recipes']

    def get_recipes(self, obj):
        """
        Возвращает список рецептов пользователя
        с ограничением по количеству.
        """
        return super().get_recipes(obj)

    def get_recipes_count(self, obj):
        """
        Возвращает общее количество рецептов у пользователя.
        """
        return super().get_recipes_count(obj)


class UserFollowSerializer(BaseUserSerializer):
    """
    Сериализатор для подписки и отписки пользователя.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = BaseUserSerializer.Meta.fields + ['is_subscribed']

    def get_is_subscribed(self, obj):
        """
        Возвращает информацию о подписке на пользователя.
        """
        return is_user_subscribed(request=self.context.get('request'), obj=obj)
