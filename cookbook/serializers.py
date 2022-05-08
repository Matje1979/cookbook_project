from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from cookbook.models import Ingredient, Rating, Recipe
import requests


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    email = serializers.EmailField(
        write_only=True,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "password2",
            "email",
            "first_name",
            "last_name",
        )

        extra_kwargs = {
            "first_name": {"required": True, "write_only": True},
            "last_name": {"required": True, "write_only": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        # Chech the email's validity.
        response = requests.get(
            f"https://api.hunter.io/v2/email-verifier?email={attrs['email']}&api_key=fef6c29aefda063bbbd82c4f8467b760f566e3cb"
        )

        if response.json()["data"]["status"] == "invalid":
            raise serializers.ValidationError({"email": "Provided email is invalid."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        user.set_password(validated_data["password"])
        user.save()

        return user


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["name"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class RecipeSerializer(serializers.ModelSerializer):
    # ingredients = IngredientSerializer(many=True)
    author = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.all())
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Ingredient.objects.all()
    )
    avg_rating = serializers.IntegerField(required=False)
    extra_kwargs = {
        "ingredients": {"allow_empty": False},
        "avg_rating": {"allow_empty": True, "required": False},
    }

    class Meta:
        model = Recipe
        # fields = "__all__"
        fields = ["name", "description", "ingredients", "author", "avg_rating"]


class RatingSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        many=False, queryset=Recipe.objects.all()
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Rating
        fields = ["recipe", "user", "rate"]
