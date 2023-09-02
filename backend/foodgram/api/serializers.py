import base64

from rest_framework.serializers import ModelSerializer, ImageField, \
    CharField, ReadOnlyField, SerializerMethodField, URLField
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer \
    as BaseUserCreateSerializer
from djoser.serializers import SetPasswordSerializer \
    as BaseSetPasswordSerializer

from recipes.models import Tag, Recipe, Ingredient, RecipeIngredient, \
    User, Subscription, FavoriteRecipe


class UserSerializer(ModelSerializer):
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
        request = self.context.get('request')
        return Subscription.objects.filter(
            author=instance, subscriber=request.user
        ).exists()


class UserCreateSerializer(BaseUserCreateSerializer):
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'password', 'first_name', 'last_name'
        )


class SetPasswordSerializer(BaseSetPasswordSerializer):

    class Meta:
        model = User
        fields = ('new_password', 'current_password', 'username')
        extra_kwargs = {
            "username": {"required": False, "allow_null": True}
        }


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = CharField(source='ingredient.name')
    measurement_unit = CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


# class Base64ImageField(ImageField):
#     def to_internal_value(self, data):
#         if isinstance(data, str) and data.startswith('data:image'):
#             format, imgstr = data.split(';base64,')
#             ext = format.split('/')[-1]

#             data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

#         return super().to_internal_value(data)


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    author = UserSerializer()
    # image = Base64ImageField()
    is_favorited = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def get_is_favorited(self, instance):
        request = self.context.get('request')
        return FavoriteRecipe.objects.filter(
            recipe=instance, user=request.user
        ).exists()


class SubscriptionRecipeSerializer(ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(ModelSerializer):
    email = ReadOnlyField(source='author.email')
    id = ReadOnlyField(source='author.id')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    is_subscribed = SerializerMethodField()
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

    def get_is_subscribed(self, instance):
        request = self.context.get('request')
        return instance.subscriber == request.user

    def get_recipes_count(self, instance):
        return instance.author.recipes.count()


class FavoriteRecipeSerializer(ModelSerializer):
    id = ReadOnlyField(source='recipe.id')
    name = ReadOnlyField(source='recipe.name')
    image = URLField(
        source='recipe.image.url', required=False, allow_null=True
    )
    cooking_time = ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'name', 'image', 'cooking_time')
