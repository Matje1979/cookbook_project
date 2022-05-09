from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User

from cookbook.models import Ingredient, Recipe
from .serializers import (
    IngredientListSerializer,
    IngredientSerializer,
    RatingSerializer,
    RecipeListSerializer,
    RecipeSerializer,
    RegisterSerializer,
)
from rest_framework import generics
from django.db.models import Count


class IngredientCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = IngredientSerializer


class RecipeCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RecipeSerializer


class RatingView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RatingSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        return Response(
            "Success! You can now get your access token and log in.",
            response.status_code,
            response.headers,
        )


#################################################
# List views
#################################################


class RecipesListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RecipeListSerializer

    def get_queryset(self):

        # Check and apply filters.
        if self.request.query_params:
            # Filter by name.
            if "name" in self.request.query_params.keys():
                return Recipe.objects.filter(name=self.request.query_params["name"])

            # Filter by description (exact).
            elif "description" in self.request.query_params.keys():
                return Recipe.objects.filter(
                    description=self.request.query_params["description"]
                )

            # Filter by ingredients (ids).
            elif "ingredients" in self.request.query_params.keys():
                return Recipe.objects.filter(
                    ingredients__in=self.request.query_params["ingredients"]
                )

            # Order by max number of ingredients.
            elif "max_ingredients" in self.request.query_params.keys():
                return Recipe.objects.annotate(
                    ingredients_count=Count("ingredients")
                ).order_by("-ingredients_count")

            # Order by min number of ingredients.
            elif "min_ingredients" in self.request.query_params.keys():
                return Recipe.objects.annotate(
                    ingredients_count=Count("ingredients")
                ).order_by("ingredients_count")

            # If filter parameter is unrecognized, return all recipes.
            else:
                return Recipe.objects.all()

        return Recipe.objects.all()


class MyRecipesListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RecipeListSerializer

    def get_queryset(self):
        queryset = Recipe.objects.filter(author=self.request.user)
        return queryset


class TopIngredientsListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = IngredientListSerializer

    def get_queryset(self):
        queryset = Ingredient.objects.top_ingredients()
        return queryset
