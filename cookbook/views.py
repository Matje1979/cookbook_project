from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .serializers import (
    IngredientSerializer,
    RatingSerializer,
    RecipeSerializer,
    RegisterSerializer,
)
from rest_framework import generics

# Create your views here.


class IngredientCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = IngredientSerializer

    # def get(self, request):
    #     content = {"message": "Helo World"}
    #     return Response(content)


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
