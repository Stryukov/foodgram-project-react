from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Sum

from recipes.models import Tag, Recipe, Ingredient, User, Subscription, \
    FavoriteRecipe, ShoppingCart
from .serializers import TagSerializer, RecipeSerializer, \
    IngredientSerializer, SubscriptionSerializer, UserSerializer, \
    UserCreateSerializer, SetPasswordSerializer, FavoriteRecipeSerializer, \
    ShopingCartSerializer, RecipeCreateSerializer
from .filters import RecipeFilter, IngredientFilter
from recipes.utils import queryset_to_csv


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        writers = self.request.user.writers.all()

        page = self.paginate_queryset(writers)
        if page is not None:
            serializer = SubscriptionSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionSerializer(
            writers,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        author = self.get_object()
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data=request.data, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save(author=author, subscriber=request.user)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DELETE':
            subscribe = get_object_or_404(
                Subscription, author=author, subscriber=request.user
            )
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return UserSerializer

    def perform_create(self, serializer):
        if self.action == 'set_password':
            serializer.save(username=self.request.user.username)


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ('name', )
    search_fields = ('name',)
    filterset_class = IngredientFilter


class TagsViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags')
    filterset_class = RecipeFilter

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            serializer = FavoriteRecipeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(recipe=recipe, user=request.user)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DELETE':
            subscribe = get_object_or_404(
                FavoriteRecipe, recipe=recipe, user=request.user
            )
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            serializer = ShopingCartSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(recipe=recipe, user=request.user)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DELETE':
            subscribe = get_object_or_404(
                ShoppingCart, recipe=recipe, user=request.user
            )
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get', ])
    def download_shopping_cart(self, request):
        user = self.request.user
        shoping_list = Ingredient.objects.filter(
            recipe__in_users_cart__user=user
            ).annotate(
                total_amount=Sum('recipeingredient__amount')
                ).order_by('name')
        ingredients_list = list(shoping_list.values_list(
            'name', 'total_amount', 'measurement_unit'
        ))
        return queryset_to_csv(ingredients_list)
