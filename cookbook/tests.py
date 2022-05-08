from django.forms import PasswordInput
from django.test import TestCase
from django.urls import reverse
from .models import Ingredient, Recipe, Rating
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient


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


#########################################################################################
# API tests
#########################################################################################


class APIViewTestCase(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(
            "Bo",
            "ex@gmail.com",
            "password321",
        )
        self.user_1.first_name = ("Bo",)
        self.user_1.last_name = ("Bobic",)

        self.user_2 = User.objects.create_user(
            "Joe",
            "xzy@gmail.com",
            "password321",
        )
        self.user_2.first_name = ("Joe",)
        self.user_2.last_name = ("Babic",)

        self.client = APIClient()
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.create_ingredient_url = reverse("add-ingredient")
        self.create_recipe_url = reverse("add-recipe")
        self.add_rating_url = reverse("add-rating")
        self.data = {
            "username": "Bob",
            "email": "bob@gmail.com",
            "password": "password321",
            "password2": "password321",
            "first_name": "Bob",
            "last_name": "Bobic",
        }

        self.access_token = self.client.post(
            self.login_url, {"username": "Bo", "password": "password321"}
        ).json()["access"]

        return super().setUp()

    def test_login_returns_jwt_tokens(self):
        """
        Check if Login view returns access and refresh tokens.
        """
        credentials = {"username": "Bo", "password": "password321"}

        response = self.client.post(self.login_url, credentials)

        self.assertEqual(response.status_code, 200)
        self.assertTrue("access" in response.json().keys())
        self.assertTrue("refresh" in response.json().keys())

    def test_registration_OK(self):
        response = self.client.post(self.register_url, self.data)
        self.assertEqual(response.status_code, 201)

    def test_registration_password_mismatch(self):
        self.data["password2"] = "password321123"
        response = self.client.post(self.register_url, self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {"password": ["Password fields didn't match."]}
        )

    def test_login_invalid_password(self):
        """
        Check if Login view FAILS to return access and refresh tokens with BAD credentials.
        """
        credentials = {"username": "Bo", "password": "FAKEpass"}

        response = self.client.post(self.login_url, credentials)

        self.assertEqual(response.status_code, 401)

    def test_registration_OK(self):
        response = self.client.post(self.register_url, self.data)
        self.assertEqual(response.status_code, 201)

    def test_registration_password_mismatch(self):
        self.data["password2"] = "password321123"
        response = self.client.post(self.register_url, self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {"password": ["Password fields didn't match."]}
        )

    def test_registration_invalid_email(self):
        self.data["email"] = "bob@yhoo.com"
        response = self.client.post(self.register_url, self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"email": ["Provided email is invalid."]})

    def test_ingredient_create_view_OK(self):
        """
        Check ingredient creation with a valid access token.
        """

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        response = self.client.post(self.create_ingredient_url, {"name": "oil"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Ingredient.objects.count(), 1)

    def test_ingredient_create_view_no_token_FAIL(self):
        """
        Check ingredient creation FAILS without an access token.
        """

        response = self.client.post(self.create_ingredient_url, {"name": "oil"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Ingredient.objects.count(), 0)

    def test_recipe_create_view_OK(self):
        """
        Check recipy creation with valid data.
        """
        self.ingredient_1 = Ingredient.objects.create(name="oil")
        self.ingredient_2 = Ingredient.objects.create(name="flour")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        response = self.client.post(
            self.create_recipe_url,
            {
                "name": "bread",
                "description": "Bla bla",
                "author": self.user_1.id,
                "ingredients": [self.ingredient_1.id, self.ingredient_2.id],
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Recipe.objects.count(), 1)
        self.assertEqual(Ingredient.objects.count(), 2)
        self.assertEqual(Recipe.objects.first().author.username, self.user_1.username)

        self.assertEqual(
            list(
                Recipe.objects.first().ingredients.all().values_list("name", flat=True)
            ),
            list(Ingredient.objects.all().values_list("name", flat=True)),
        )

    def test_rating_view(self):
        """
        Rating with valid data.
        """
        self.ingredient_1 = Ingredient.objects.create(name="oil")
        self.ingredient_2 = Ingredient.objects.create(name="flour")
        self.ingredient_3 = Ingredient.objects.create(name="sugar")

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.client.post(
            self.create_recipe_url,
            {
                "name": "bread",
                "description": "Bla bla",
                "author": self.user_1.id,
                "ingredients": [self.ingredient_1.id, self.ingredient_2.id],
            },
        )
        self.client.post(
            self.create_recipe_url,
            {
                "name": "Cake",
                "description": "Delicious cake",
                "author": self.user_2.id,
                "ingredients": [
                    self.ingredient_1.id,
                    self.ingredient_2.id,
                    self.ingredient_3.id,
                ],
            },
        )
        # User 1 rating cake. Cannot rate bread because users cannot rate their own resipes.
        response_1 = self.client.post(
            self.add_rating_url,
            {"recipe": Recipe.objects.get(name="Cake").id, "rate": 5},
        )

        # User 2 rating bread.
        # First must fetch access token for user 2 to authenticate as user 2.
        self.access_token_2 = self.client.post(
            self.login_url, {"username": "Joe", "password": "password321"}
        ).json()["access"]

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token_2)

        response_2 = self.client.post(
            self.add_rating_url,
            {"recipe": Recipe.objects.get(name="bread").id, "rate": 4},
        )

        self.assertEqual(response_1.status_code, 201)
        self.assertEqual(response_2.status_code, 201)

        self.assertEqual(Rating.objects.count(), 2)

    def test_rating_view_self_rating_FAIL(self):
        """
        Rating ones own recipe must fail.
        """
        self.ingredient_1 = Ingredient.objects.create(name="oil")
        self.ingredient_2 = Ingredient.objects.create(name="flour")

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.client.post(
            self.create_recipe_url,
            {
                "name": "bread",
                "description": "Bla bla",
                "author": self.user_1.id,
                "ingredients": [self.ingredient_1.id, self.ingredient_2.id],
            },
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        with self.assertRaises(ValidationError) as e:
            self.client.post(
                self.add_rating_url,
                {"recipe": Recipe.objects.get(name="bread").id, "rate": 5},
            )

        self.assertEqual(e.exception.messages[0], "User cannot rate its own recipe!")
        self.assertEqual(Rating.objects.count(), 0)
