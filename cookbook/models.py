from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Count


class IngredientQuerySet(models.QuerySet):
    def top_ingredients(self):
        return self.annotate(recipe_count=Count("recipe")).order_by("-recipe_count")[:5]


class Ingredient(models.Model):
    name = models.CharField(max_length=50, unique=True)

    objects = IngredientQuerySet.as_manager()

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=300, unique=True)
    ingredients = models.ManyToManyField(Ingredient)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def avg_rating(self):
        ratings_list = list(self.ratings.values_list("rate", flat=True))
        if len(ratings_list) > 0:
            return sum(ratings_list) / len(ratings_list)
        else:
            return 0


class Rating(models.Model):
    rate = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ratings")

    class Meta:
        unique_together = ["user", "recipe"]

    def clean(self, *args, **kwargs):
        if self.user == self.recipe.author:
            raise ValidationError("User cannot rate its own recipe!")
        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Rating of {self.recipe} by {self.user}"
