from rest_framework import serializers
from .models import Article,ArticleCategory,Comment
from rest_framework.validators import UniqueValidator
from apps.user.models import User



class CategorySerialize(serializers.ModelSerializer):

    class Meta:
        model = ArticleCategory
        fields = ["name"]


class PublishSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    blogId =serializers.IntegerField(required=False)
    tags = serializers.ListField(child=serializers.CharField(max_length=100),required=False)
    pics = serializers.URLField(required=False)


    class Meta:
        model = Article
        fields = ("id","title","text","pics","blogId","tags")


class Return_User_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","avatar"]

class Article_to_User_Serializer(serializers.ModelSerializer):
    author = Return_User_Serializer()
    class Meta:
        model = Article
        fields = ["author"]

class CommentSerializer(serializers.ModelSerializer):
    article = Article_to_User_Serializer()
    author = Return_User_Serializer()
    class Meta:
        model = Comment
        fields = ["article","author","content"]

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArticleCategory
        fields = ["name"]

class Tag_Blog_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ("id","author","title","thumbnail")
