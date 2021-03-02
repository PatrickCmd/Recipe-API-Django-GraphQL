import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Q

from .models import Category, Recipe, Ingredient, RecipeVote
from auth_user.schema import UserType


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__"


class RecipeType(DjangoObjectType):
    class Meta:
        model = Recipe
        fields = "__all__"


class IngredientType(DjangoObjectType):
    class Meta:
        model = Ingredient
        fields = "__all__"


class Query(graphene.ObjectType):
    category = graphene.Field(CategoryType, id=graphene.Int(), name=graphene.String())
    # Add the search parameter inside our links field
    # Add the first and Skip parameters to enable pagination
    all_categories = graphene.List(
        CategoryType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )

    recipe = graphene.Field(RecipeType, id=graphene.Int())

    all_recipes = graphene.List(
        RecipeType,
        first=graphene.Int(),
        skip=graphene.Int(),
    )

    def resolve_all_categories(self, info, search=None, first=None, skip=None, **kwargs):
        qs = Category.objects.all()
        if search:
            filter = (
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
            qs = qs.filter(filter)
        
        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]
        
        # Returning queryset result
        return qs
    
    def resolve_category(self, info, id=None, name=None):
        if id is not None:
            return Category.objects.get(pk=id)
        
        if name is not None:
            return Category.objects.get(name=name)
    
    def resolve_all_recipes(self, info, first=None, skip=None):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in!")
        
        # We can easily optimize query count in the resolve method
        qs = Recipe.objects.select_related("category").filter(owner=user)

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return qs
    
    def resolve_recipe(self, info, id):
        try:
            recipe = Recipe.objects.get(pk=id)
        except Recipe.DoesNotExist:
            raise GraphQLError("Invalid Recipe ID!")
        return recipe


class CreateCatgory(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        name = graphene.String(required=True)
        description = graphene.String()

    # The class attributes define the response of the mutation
    category = graphene.Field(CategoryType)

    def mutate(self, info, name, description):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to complete this action!")
        category = Category.objects.create(
            name=name,
            description=description,
            owner=user,
        )
        # Notice we return an instance of this mutation
        return CreateCatgory(category=category)


class UpdateCategory(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        description = graphene.String()
    
    category = graphene.Field(CategoryType)

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to complete this action!")

        id = kwargs.get('id')
        name = kwargs.get('name', None)
        description = kwargs.get('description', None)

        try:
            category = Category.objects.get(pk=id)
        except Category.DoesNotExist:
            raise GraphQLError("Invalid category ID!")
            
        if category.owner != user:
            raise GraphQLError("You are not permitted to update this category")

        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
        category.save()

        return UpdateCategory(category=category)


class DeleteCategory(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    cat_id = graphene.Int()

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to complete this action!")
        id = kwargs.get('id')
        
        try:
            category = Category.objects.get(pk=id)
        except Category.DoesNotExist:
            raise GraphQLError("Invalid category ID!")

        if category.owner != user:
            raise GraphQLError("You are not permitted to delete this category")

        category.delete()

        return DeleteCategory(cat_id=id)


class CreateRecipe(graphene.Mutation):
    class Arguments:
        cat_id = graphene.Int(required=True)
        title = graphene.String(required=True)
        description = graphene.String()
        is_public = graphene.Boolean()
    
    recipe = graphene.Field(RecipeType)

    def mutate(self, info, **kwargs):
        user = info.context.user
        cat_id = kwargs.get("cat_id")
        title = kwargs.get('title')
        description = kwargs.get('description')
        is_public = kwargs.get('is_public', False)

        if user.is_anonymous:
            raise GraphQLError("You must be logged in to complete this action!")
        
        category = Category.objects.filter(pk=cat_id)
        if not category.exists():
            raise GraphQLError("Invalid category id")
        recipe = Recipe.objects.create(
            owner=user,
            category=category[0],
            title=title,
            description=description,
            is_public=is_public,
        )
        return CreateRecipe(recipe=recipe)


class UpdateRecipe(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        is_public = graphene.Boolean()
    
    recipe = graphene.Field(RecipeType)

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to complete this action!")

        try:
            recipe = Recipe.objects.get(pk=id)
        except Recipe.DoesNotExist:
            raise GraphQLError("Invalid Recipe ID!")
            
        if recipe.owner != user:
            raise GraphQLError("You are not permitted to update this recipe")
        
        kwargs.pop("id")
        for k, v in kwargs.items():
            if v is not None or v != "":
                setattr(recipe, k, v)
        recipe.save()

        return UpdateRecipe(recipe=recipe)


class DeleteRecipe(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    recipe_id = graphene.Int()

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to complete this action!")
        id = kwargs.get('id')
        
        try:
            recipe = Recipe.objects.get(pk=id)
        except Recipe.DoesNotExist:
            raise GraphQLError("Invalid Recipe ID!")

        if recipe.owner != user:
            raise GraphQLError("You are not permitted to delete this recipe")

        recipe.delete()

        return DeleteRecipe(recipe_id=id)


class CreateIngredient(graphene.Mutation):
    class Arguments:
        recipe_id = graphene.Int(required=True)
        name = graphene.String(required=True)
        amount = graphene.Float(required=True)
        instruction_notes = graphene.String()
    
    ingredient = graphene.Field(IngredientType)

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to complete this action!")
        recipe_id = kwargs.get('recipe_id')
        name = kwargs.get('name')
        amount = kwargs.get('amount')
        instruction_notes = kwargs.get('instruction_notes')

        recipe = Recipe.objects.filter(pk=recipe_id)

        if not recipe.exists():
            raise GraphQLError("Invalid recipe ID!")
        ingredient = Ingredient.objects.create(
            recipe=recipe[0],
            name=name,
            amount=amount,
            instruction_notes=instruction_notes,
        )

        return CreateIngredient(ingredient=ingredient)


class CreateRecipeVote(graphene.Mutation):
    user = graphene.Field(UserType)
    recipe = graphene.Field(RecipeType)

    class Arguments:
        recipe_id = graphene.Int(required=True)
    
    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to complete this action!")

        recipe_id = kwargs.get('recipe_id')

        try:
            recipe = Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist:
            raise GraphQLError("Invalid Recipe ID!")

        RecipeVote.objects.create(
            user=user,
            recipe=recipe,
        )

        return CreateRecipeVote(user=user, recipe=recipe)


class Mutation:
    create_category = CreateCatgory.Field()
    create_recipe = CreateRecipe.Field()
    create_ingredient = CreateIngredient.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()
    update_recipe = UpdateRecipe.Field()
    delete_recipe = DeleteRecipe.Field()
    create_recipe_vote = CreateRecipeVote.Field()
