from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Sum
from django.db import IntegrityError
from rest_framework.permissions import AllowAny, IsAuthenticated

from recipes.models import Tag, Recipe, Ingredient, User, Subscription, \
    FavoriteRecipe, ShoppingCart
from .serializers import TagSerializer, RecipeSerializer, \
    IngredientSerializer, SubscriptionSerializer, UserSerializer, \
    SetPasswordSerializer, FavoriteRecipeSerializer, \
    ShopingCartSerializer, RecipeCreateSerializer, UserCreateSerializer
from .filters import RecipeFilter, IngredientFilter
from recipes.utils import queryset_to_csv
from .permissions import IsOwnerOrAdminOrReadOnly, ReadOnly


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """
        Получение списка авторов рецептов,
        на которых подписан пользователь их рецепты.
        """
        limit_recipes = int(request.GET.get('recipes_limit', 0))
        writers = self.request.user.writers.all()

        page = self.paginate_queryset(writers)
        if page is not None:
            serializer = SubscriptionSerializer(
                page,
                many=True,
                context={'request': request}
            )
            paginated_data = self.get_paginated_response(serializer.data).data

            return self.limit_recipes(paginated_data, limit_recipes)

        serializer = SubscriptionSerializer(
            writers,
            many=True,
            context={'request': request}
        )

        return self.limit_recipes(serializer.data, limit_recipes)

    def limit_recipes(self, data, limit):
        """
        Ограничение количесва рецептов в выводе.
        """
        for result in data['results']:
            result['recipes'] = result['recipes'][:limit]

        return Response(data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """
        Подписка/отписка на автора рецептов.
        """
        author = self.get_object()

        if request.method == 'POST':
            try:
                serializer = SubscriptionSerializer(
                    data=request.data, context={'request': request}
                )
                if serializer.is_valid():
                    serializer.save(author=author, subscriber=request.user)
                    return Response(
                        serializer.data, status=status.HTTP_201_CREATED
                    )
            except IntegrityError as error:
                return Response(
                    {'errors': str(error)}, status=status.HTTP_400_BAD_REQUEST
                )

        if request.method == 'DELETE':
            try:
                subscribe = Subscription.objects.get(
                    author=author, subscriber=request.user
                )
            except Subscription.DoesNotExist as error:
                return Response(
                    {'errors': str(error)}, status=status.HTTP_400_BAD_REQUEST
                )
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return UserSerializer

    def perform_create(self, serializer, *args, **kwargs):
        if self.action == 'set_password':
            serializer.save(username=self.request.user.username)
        else:
            return super().perform_create(serializer, *args, **kwargs)


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ('name', )
    search_fields = ('name',)
    filterset_class = IngredientFilter
    permission_classes = (IsOwnerOrAdminOrReadOnly,)


class TagsViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class RecipesViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = (IsOwnerOrAdminOrReadOnly,)

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()

        if request.method == 'POST':
            return self.add_related_entry(
                request, recipe, FavoriteRecipeSerializer
            )

        if request.method == 'DELETE':
            return self.delete_related_entry(request, recipe, FavoriteRecipe)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()

        if request.method == 'POST':
            return self.add_related_entry(
                request, recipe, ShopingCartSerializer
            )

        if request.method == 'DELETE':
            return self.delete_related_entry(request, recipe, ShoppingCart)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=['get', ],
        permission_classes=(IsAuthenticated,)
    )
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

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()

    def delete_related_entry(self, request, recipe, related_model):
        """
        Удаляем запись из связанной модели.
        """
        try:
            instance = related_model.objects.get(
                recipe=recipe, user=request.user
            )
        except related_model.DoesNotExist as error:
            return Response(
                {'errors': str(error)}, status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def add_related_entry(self, request, recipe, serializer):
        """
        Добавляем запись в связанную модель.
        """
        try:
            serializer = serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(recipe=recipe, user=request.user)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        except IntegrityError as error:
            return Response(
                {'errors': str(error)}, status=status.HTTP_400_BAD_REQUEST
            )
