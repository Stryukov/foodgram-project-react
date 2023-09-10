import base64

from rest_framework.serializers import ModelSerializer, ImageField, \
    CharField, ReadOnlyField, SerializerMethodField, URLField, \
    PrimaryKeyRelatedField, ValidationError
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer \
    as BaseUserCreateSerializer
from djoser.serializers import SetPasswordSerializer \
    as BaseSetPasswordSerializer

from recipes.models import Tag, Recipe, Ingredient, RecipeIngredient, \
    User, Subscription, FavoriteRecipe, ShoppingCart


class UserSerializer(ModelSerializer):
    """
    Для обработки моделя пользователей.
    """
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, instance):
        """
        Возвращает статус подписки текущего пользователя.
        """
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return (
            Subscription.objects.filter(
                author=instance, subscriber=request.user
            ).exists()
            and request.user.is_authenticated
        )


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Для создания пользователя.
    """

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'password', 'first_name', 'last_name'
        )


class SetPasswordSerializer(BaseSetPasswordSerializer):
    """
    Для изменения пароля.
    """

    class Meta:
        model = User
        fields = ('new_password', 'current_password', 'username')
        extra_kwargs = {
            "username": {"required": False, "allow_null": True}
        }


class TagSerializer(ModelSerializer):
    """
    Для обработке запросов модели тегов.
    """

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    """
    Обработка запросов по ингредиентам.
    """

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(ModelSerializer):
    """
    Для получения данных из связаной таблицы рецептов и ингредиентов.
    """
    id = ReadOnlyField(source='ingredient.id')
    name = CharField(source='ingredient.name')
    measurement_unit = CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class Base64ImageField(ImageField):
    """
    Для загрузки изображения рецепта.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(ModelSerializer):
    """
    Обработка запросов по рецептам.
    """
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    author = UserSerializer()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = URLField(
        source='image.url', required=False, allow_null=True
    )

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def get_is_favorited(self, instance):
        """
        Возвращает статус избранного рецепта.
        """
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            recipe=instance, user=request.user
        ).exists()

    def get_is_in_shopping_cart(self, instance):
        """
        Возвращает статус рецепта в корзине.
        """
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=instance, user=request.user
        ).exists()


class SubscriptionRecipeSerializer(ModelSerializer):
    """
    Обработка запросов по подпискам и связаной модели рецептов.
    """
    image = URLField(
        source='image.url', required=False, allow_null=True
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(ModelSerializer):
    """
    Обработка запросов по подпискам на авторов рецептов.
    """
    email = ReadOnlyField(source='author.email')
    id = ReadOnlyField(source='author.id')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    is_subscribed = ReadOnlyField(source='author.is_subscribed')
    recipes = SubscriptionRecipeSerializer(
        many=True, source='author.recipes', required=False
    )
    recipes_count = SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, instance):
        """
        Подсчет количеста рецептов автора
        """
        return instance.author.recipes.count()


class FavoriteRecipeSerializer(ModelSerializer):
    """
    Обработка запросов избранных рецептов.
    """
    id = ReadOnlyField(source='recipe.id')
    name = ReadOnlyField(source='recipe.name')
    image = URLField(
        source='recipe.image.url', required=False, allow_null=True
    )
    cooking_time = ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShopingCartSerializer(ModelSerializer):
    """
    Обработка запросов рцептов в корзине.
    """
    id = ReadOnlyField(source='recipe.id')
    name = ReadOnlyField(source='recipe.name')
    image = URLField(
        source='recipe.image.url', required=False, allow_null=True
    )
    cooking_time = ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeIngredientsCreateSerializer(ModelSerializer):
    """
    Для обработки связанной таблици ингредиентов при создании рецепта.
    """
    id = PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        """
        Валидация ингредиентов. Кол-во ингредиента должно быть больше нуля.
        """
        if not value:
            raise ValidationError(
                'Количество ингредиента должно быть больше нуля.'
            )
        return value


class RecipeCreateSerializer(ModelSerializer):
    """
    Обработка запроса на создание рецепта.
    """
    ingredients = RecipeIngredientsCreateSerializer(
        many=True, source='recipe_ingredients'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'cooking_time',
            'ingredients',
            'tags',
            'image'
        )

    def create(self, validated_data):
        """
        Переопределен метод, т.к. джанго не умеет добавлять записи
        в связанные модели.
        """
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = super().create(validated_data)
        for ingredient_data in ingredients:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient_data)
        return recipe

    def update(self, instance, validated_data):
        """
        Переопределен метод, т.к. джанго не умеет добавлять записи
        в связанные модели.
        """
        ingredients = validated_data.pop('recipe_ingredients')
        super().update(instance, validated_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient_data in ingredients:
            RecipeIngredient.objects.create(recipe=instance, **ingredient_data)
        return instance

    def validate_ingredients(self, value):
        """
        Валидация ингредиентов. Рецепт не может быть без ингредиентов.
        """
        if not value:
            raise ValidationError('Добавьте ингредиенты.')
        return value

    def validate_cooking_time(self, value):
        """
        Валидация времени готовки. Не должно быть нулем.
        """
        if not value:
            raise ValidationError(
                'Время приготовления должно быть больше нуля.'
            )
        return value
