from rest_framework import serializers
from .models import Article,ArticleCategory,Comment
from rest_framework.validators import UniqueValidator
from apps.user.models import User,Recommand_Detail



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


class Tag_Detail_Serializer(serializers.ModelSerializer):

    class Meta:
        model = ArticleCategory
        fields = ["name","is_great"]

class Blog_Detail_Serializer(serializers.ModelSerializer):
    category = Tag_Detail_Serializer(many=True)
    class Meta:
        model = Article
        fields = ["id","pub_time","title","text","thumbnail","category"]



class CommentList_ArticleAuthor_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username"]

class CommentList_Article_Serializer(serializers.ModelSerializer):
    author = CommentList_ArticleAuthor_Serializer()
    class Meta:
        model = Article
        fields = ["author"]

class CommentList_Author_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","avatar"]


class CommentList_Serializer(serializers.ModelSerializer):
    article = CommentList_Article_Serializer()
    author = CommentList_Author_Serializer()
    class Meta:
        model = Comment
        fields = ["content","author","article"]

class HotList_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","avatar"]




class BlogDetail_User_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","avatar"]



class BlogDetail_Recommend_User_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username"]



class BlogDetail_Serializer(serializers.ModelSerializer):
    category = Tag_Detail_Serializer(many=True)
    author = BlogDetail_User_Serializer()
    # recommand_detail_set = BlogDetail_Recommend_Serializer(many=True)
    class Meta:
        model = Article
        fields = ["id","pub_time","thumbnail","title","text",
                  "category","author",
                  "comment_count"]

class BlogDetail_OwnBlog_Serializer(serializers.ModelSerializer):
    author = BlogDetail_User_Serializer()
    category = Tag_Detail_Serializer(many=True)
    class Meta:
        model = Article
        fields = ["id","pub_time","thumbnail","title","text",
                  "category","author",
                  "comment_count"]