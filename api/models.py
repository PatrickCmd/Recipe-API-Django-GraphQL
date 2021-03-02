from django.conf import settings
from django.db import models


class Category(models.Model):

    class Meta:
        verbose_name_plural = 'categories'
    
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    
class Recipe(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name="recipes",
                              on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="ingredients",
                               on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.FloatField()
    instruction_notes = models.TextField()

    def __str__(self):
        return self.name


class RecipeVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, related_name="votes",
                               on_delete=models.CASCADE)
    
    def __str__(self):
        return f"<{self.pk}-{self.recipe.title}>"
