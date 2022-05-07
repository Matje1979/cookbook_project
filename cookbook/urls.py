from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from . import views

urlpatterns = [
    path("login/", jwt_views.TokenObtainPairView.as_view(), name="login"),
    path(
        "add_ingredient/", views.IngredientCreateView.as_view(), name="add-ingredient"
    ),
    path("add_recipe/", views.RecipeCreateView.as_view(), name="add-recipe"),
    path("register/", views.RegisterView.as_view(), name="register"),
]
