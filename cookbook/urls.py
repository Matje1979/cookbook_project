from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", jwt_views.TokenObtainPairView.as_view(), name="login"),
    path(
        "add_ingredient/", views.IngredientCreateView.as_view(), name="add-ingredient"
    ),
    path("add_recipe/", views.RecipeCreateView.as_view(), name="add-recipe"),
    path("add_rating/", views.RatingView.as_view(), name="add-rating"),
    path("recipes_list/", views.RecipesListView.as_view(), name="recipes-list"),
    path(
        "top_ingredients/",
        views.TopIngredientsListView.as_view(),
        name="top-ingredients",
    ),
    path("my_recipes/", views.MyRecipesListView.as_view(), name="my-recipes"),
]
