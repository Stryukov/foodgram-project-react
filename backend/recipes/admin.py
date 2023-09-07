from django.contrib import admin

from .models import Tag, Recipe, Ingredient, RecipeIngredient, \
    Subscription, ShoppingCart, FavoriteRecipe


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInLine, )
    list_display = ('name', 'author')
    list_filter = ('author', 'tags', 'name')
    search_fields = ('name',)
    fields = (
        'name', 'author', 'tags', 'text', 'cooking_time', 'image',
        'count_favorites'
    )
    readonly_fields = ('count_favorites',)

    def count_favorites(self, instance):
        count = FavoriteRecipe.objects.filter(
            recipe=instance
        ).count()
        return count


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('author', 'subscriber')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
