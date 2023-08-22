from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UsersViewSet


app_name = 'api'

router = DefaultRouter()


router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('users', UsersViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = (path('', include(router.urls)),
               path('auth/', include('djoser.urls.authtoken')),)
