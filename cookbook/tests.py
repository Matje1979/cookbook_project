from django.test import TestCase
from .models import Ingredient, Recipe, Rating
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class CookbookTestCase(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(
            username="user 1", email="user_1@example.com", password="pass321"
        )
        self.recipe_1 = Recipe.objects.create(
            name="Recipe 1", description="Description for Recipe 1", author=self.user_1
        )
        return super().setUp()


class IngredientQuerySetTestCase(CookbookTestCase):
    def setUp(self):
        super().setUp()

        self.ingred_1 = Ingredient.objects.create(name="Ingredient 1")
        self.ingred_2 = Ingredient.objects.create(name="Ingredient 2")
        self.ingred_3 = Ingredient.objects.create(name="Ingredient 3")
        self.ingred_4 = Ingredient.objects.create(name="Ingredient 4")
        self.ingred_5 = Ingredient.objects.create(name="Ingredient 5")
        self.ingred_6 = Ingredient.objects.create(name="Ingredient 6")
        self.ingred_7 = Ingredient.objects.create(name="Ingredient 7")

        self.recipe_2 = Recipe.objects.create(
            name="Recipe 2", description="Description for Recipe 2", author=self.user_1
        )
        self.recipe_3 = Recipe.objects.create(
            name="Recipe 3", description="Description for Recipe 3", author=self.user_1
        )
        self.recipe_4 = Recipe.objects.create(
            name="Recipe 4", description="Description for Recipe 4", author=self.user_1
        )
        self.recipe_5 = Recipe.objects.create(
            name="Recipe 5", description="Description for Recipe 5", author=self.user_1
        )
        self.recipe_6 = Recipe.objects.create(
            name="Recipe 6", description="Description for Recipe 6", author=self.user_1
        )
        self.recipe_7 = Recipe.objects.create(
            name="Recipe 7", description="Description for Recipe 7", author=self.user_1
        )

        self.recipe_1.ingredients.add(self.ingred_1, self.ingred_2, self.ingred_5)
        self.recipe_2.ingredients.add(self.ingred_1, self.ingred_5)
        self.recipe_3.ingredients.add(self.ingred_1, self.ingred_2, self.ingred_3)
        self.recipe_5.ingredients.add(self.ingred_1, self.ingred_2, self.ingred_3)
        self.recipe_6.ingredients.add(self.ingred_1, self.ingred_2, self.ingred_6)
        self.recipe_7.ingredients.add(self.ingred_1, self.ingred_5)

        return

    def test_top_ingredients(self):
        top_ingredients = Ingredient.objects.top_ingredients()
        self.assertEqual(len(top_ingredients), 5)
        self.assertEqual(
            list(top_ingredients.values_list("name", flat=True)),
            [
                "Ingredient 1",
                "Ingredient 2",
                "Ingredient 5",
                "Ingredient 3",
                "Ingredient 6",
            ],
        )


class RecipeTestCase(CookbookTestCase):
    def setUp(self):
        super().setUp()

        self.user_2 = User.objects.create(
            username="user 2", email="user_2@example.com", password="pass321"
        )
        self.user_3 = User.objects.create(
            username="user 3", email="user_3@example.com", password="pass321"
        )

        self.rating_2 = Rating.objects.create(
            rate=5, user=self.user_2, recipe=self.recipe_1
        )
        self.rating_3 = Rating.objects.create(
            rate=3, user=self.user_3, recipe=self.recipe_1
        )
        return

    def test_invalid_rating_recipe_author(self):
        with self.assertRaises(ValidationError) as e:
            self.rating_1 = Rating.objects.create(
                rate=3, user=self.user_1, recipe=self.recipe_1
            )
        self.assertEqual(e.exception.messages[0], "User cannot rate its own recipe!")

    def test_invalid_rating_out_of_range(self):
        pass

    def test_avg_rating(self):
        self.assertEqual(self.recipe_1.avg_rating(), 4)
