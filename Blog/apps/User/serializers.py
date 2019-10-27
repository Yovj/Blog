from django.core.cache import cache
from .models import User,Relation_Detail
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100)
    class Meta:
        model = User
        fields = ("name","email","password")

class UpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100,required=False)
    email = serializers.EmailField(required=False,validators=[UniqueValidator(queryset=User.objects.all())])
    class Meta:
        model = User
        fields = ["id","name","avatar","email"]


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ("email","password")


class LoginReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","username","email","avatar")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username","email","avatar")
#
#
#
class Relation_Time_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","avatar"]

class ListUserReturnSerializer(serializers.ModelSerializer):
    relation_who = Relation_Time_Serializer()
    class Meta:
        model = Relation_Detail
        fields = ("date_relation","relation_who")


