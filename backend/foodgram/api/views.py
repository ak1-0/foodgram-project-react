from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from djoser.views import UserViewSet

from recipes.models import Ingredient, Recipe, Tag
from users.models import User

from .filters import IngredientSearchFilter, RecipeSearchFilter
from .mixins import (BaseRecipeMixin,
                     FavoriteRecipeMixin,
                     ShoppingCartMixin,
                     SubscribeMixin,
                     SetPasswordMixin,
                     SubscriptionsMixin)
from .pagination import CustomPagination
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import (IngredientSerializer,
                          RecipeCreateSerializer,
                          FullRecipeSerializer,
                          TagSerializer,
                          UsersSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Представление ингредиентов: список, создание, изменение и удаление.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class TagViewSet(viewsets.ModelViewSet):
    """
    Представление тегов: список, создание, изменение и удаление.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class UsersViewSet(UserViewSet, viewsets.GenericViewSet,
                   SubscriptionsMixin,
                   SubscribeMixin,
                   SetPasswordMixin):
    """
    Представление пользователей: список, профиль, подписки, пароль.
    """
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = CustomPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet,
                    FavoriteRecipeMixin,
                    ShoppingCartMixin,
                    BaseRecipeMixin):
    """
    Представление рецептов: список, создание,
    изменение, удаление, избранное, корзина.
    """
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeSearchFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return FullRecipeSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post'])
    def add_to_favorites(self, request, pk):
        return self.favorite_recipe(request, pk)

    @action(detail=True, methods=['delete'])
    def remove_from_favorites(self, request, pk):
        return self.remove_from_favorites(request, pk)

    @action(detail=True, methods=['post'])
    def add_to_shopping_cart(self, request, pk):
        return self._add_to_shopping_cart(request, pk)

    @action(detail=True, methods=['delete'])
    def remove_from_shopping_cart(self, request, pk):
        return self.remove_from_shopping_cart(request, pk)
