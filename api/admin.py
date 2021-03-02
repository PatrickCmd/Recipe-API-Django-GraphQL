from django.contrib import admin

from .models import Category, Recipe, Ingredient, RecipeVote


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "description",
    )
    search_fields = (
        "name",
        "owner"
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "owner",
        "category",
        "description",
        "is_public",
    )
    search_fields = (
        "title",
        "category",
        "description",
        "owner",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "recipe",
        "amount",
        "instruction_notes",
    )
    search_fields = (
        "name",
        "recipe",
    )


admin.site.register(RecipeVote)
