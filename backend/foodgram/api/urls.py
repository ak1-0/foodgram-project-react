from rest_framework import routers
from django.urls import path, include

from api.views import index, CustomUserViewSet

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)

urlpatterns = [
    path('index', index),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
