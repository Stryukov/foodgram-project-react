from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(
        User, related_name='recipes', on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    image = models.ImageField(upload_to='images')
    name = models.CharField(max_length=200)
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()
    is_favorited = models.ManyToManyField(User, through='FavoriteRecipe')

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, related_name='recipe_ingredients', on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()


class Subscription(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers'
    )
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='writers'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'subscriber'],
                name='unique_subscribe',
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('subscriber')),
                name='check_subscribe_youself',
            )
        ]

    def __str__(self) -> str:
        return self.subscriber.get_username()


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='in_favorite'
    )

    class Meta:
        unique_together = ('user', 'recipe')
