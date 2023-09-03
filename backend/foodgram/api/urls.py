from django.urls import path, include
from rest_framework import routers

from api.views import CustomUserViewSet, TagsViewSet, RecipesViewSet, \
    IngredientsViewSet


router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('tags', TagsViewSet)
router.register('recipes', RecipesViewSet)
router.register('ingredients', IngredientsViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
