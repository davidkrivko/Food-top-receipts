from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password", "email", "first_name")
        extra_kwargs = {"password": {"write_only": True}}


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "password")
        extra_kwargs = {"password": {"write_only": True}}
