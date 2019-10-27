from django.shortcuts import render
from django.views.decorators.http import require_POST
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .serializer import PublishSerializer,TagSerializer
from utils import restful
from apps.user.models import User,Relation_Detail
from .models import Article,ArticleCategory
from .serializer import Return_User_Serializer,Tag_Blog_Serializer
from django.db.models import Q,Count
# Create your views here.


hot = 3000

@api_view(['POST'])
def publish_Blog(request):
    data = request.data
    serializer = PublishSerializer(data=data)

    if serializer.is_valid():
        try:
            user_id = serializer.data.get("id")
            user = User.objects.get(pk=user_id)
        except:
            return restful.fail(message="用户不存在")
        blog_id = serializer.data.get("blogId")
        if not blog_id:
            # 新建博文
            title = serializer.data.get("title")
            text = serializer.data.get("text")
            tags = serializer.data.get("tags")
            print(tags)
            thumbnail = serializer.data.get("pics")
            article = Article.objects.create(title=title,text=text,author=user,thumbnail=thumbnail)
            data = {"id":article.id}
            if not tags:
                return restful.ok(message="博文创建成功，没有标签分配",data=data)
            tags_dict = {}
            for tag in tags:
                try:
                    blog_tag = ArticleCategory.objects.filter(name=tag).first()
                    article.category.add(blog_tag)
                except:
                     # 不存在tag，则创建
                    print("不存在")
                    blog_tag = ArticleCategory.objects.create(name=tag,count=1)
                    article.category.add(blog_tag)
                if blog_tag.count >= hot:
                    tag_item = {"name":tag,"isHot":True}
                else:
                    tag_item = {"name":tag,"isHot":False}
                tags_dict[tag] = tag_item
            article.save()
            print(data)
            data.update({"tags":tags_dict})
            print("data",data)
            print("tags",tags_dict)
            return restful.ok(message="博文创建成功",data=data)
        else:
            # 修改博文
            try:
                article = Article.objects.get(pk=blog_id)
            except:
                return restful.fail(message="博文不存在")
            title = serializer.data.get("title")
            text = serializer.data.get("text")
            tags = serializer.data.get("tags")
            print(tags)
            thumbnail = serializer.data.get("pics")
            data = {"id":blog_id}
            article.title = title
            article.text = text
            if thumbnail:
                article.thumbnail = thumbnail
            if tags:
                tags_dict = {}
                for tag in tags:
                    try:
                        article_category = ArticleCategory.objects.filter(name=tag).first()
                        article.category.add(article_category)
                    except:
                        article_category = ArticleCategory.objects.create(name=tag,count=1)
                        article.category.add(article_category)
                    if article_category.count >= hot:
                        tag_item = {"name":tag,"isHot":True}
                    else:
                        tag_item = {"name":tag,"isHot":False}
                    tags_dict[tag] = tag_item
                data.update(tags_dict)
                article.save()
            return restful.ok(message="博文修改成功",data=data)
    else:
        print(serializer.errors)
        return restful.fail(message="参数格式错误")


@api_view(['POST'])
def delete_Blog(request):
    data = request.data
    user_id = data.get("user_id")
    blog_id = data.get("blog_id")
    if user_id and blog_id:
        try:
            blog = Article.objects.get(pk=blog_id)
            user = User.objects.get(pk=user_id)
        except:
            return restful.fail(message="博文或用户不存在")
        auth_id = blog.author.id
        if user.is_superuser or auth_id == user_id:
            # 删除博文
            print(blog.category.all())
            for tag in blog.category.all():
                tag.count -= 1
                if tag.count == 0:
                    tag.delete()
            blog.delete()
            return restful.ok(message="删除成功")
        else:
            # 提示没有权限
            return restful.fail(message="用户没有权限，删除失败")


    else:
        return restful.fail(message="参数格式错误")



@api_view(['POST'])
def vist_tag(request):
    name = request.data.get("name")
    if name:
        tag = ArticleCategory.objects.filter(name=name).first()
        if not tag:
            return restful.fail(message="标签不存在")
        tag.count += 1
        tag.save()
        return restful.ok(message="访问成功",data=tag.count)
    else:
        return restful.fail(message="请传入标签名称")


@api_view(['POST']) # 未考虑page
def get_tag_UerList(request):
    id = request.data.get("id") # 用户id
    pagenum = request.data.get("pagenum")
    pagesize = request.data.get("pagesize")
    name = request.data.get("name") # 便签名

    if id and name:
        try:
            user = User.objects.get(pk=id)
            tag = ArticleCategory.objects.get(name=name)
        except:
            return restful.fail(message="用户或便签不存在")


        related_users = User.objects.filter(Q(article__category=tag) & ~Q(id=id)).all()
        serializer = Return_User_Serializer(related_users,many=True)
        focused_user = Relation_Detail.objects.filter(who_relation=user,relation_type=1).all()
        data = serializer.data
        for dict_item in data:
            id_dict = dict_item["id"]
            is_focus = Relation_Detail.objects.filter(who_relation=user,relation_who__id=id_dict,relation_type=1).first()
            if is_focus:
                dict_item["isFocused"] = 1
            else:
                dict_item["isFocused"] = 0
        return restful.ok(message="成功",data=data)
    else:
        return restful.fail(message="传入参数错误")


@api_view(['POST']) # 未考虑page
def get_tagList(request):
    pagenum = request.data.get("pagenum")
    pagesize = request.data.get("pagesize")
    type_operation = request.data.get("type")

    if type_operation == 0: # 热门
        tags = ArticleCategory.objects.all().order_by("count")
        serializer = TagSerializer(tags,many=True)

    elif type_operation == 1: # 最新
        tags = ArticleCategory.objects.all().order_by("-time")
        serializer = TagSerializer(tags,many=True)
    else:
        return restful.fail(message="传入参数错误")
    data = {}
    data["tags"] = serializer.data
    data["total"] = ArticleCategory.objects.aggregate(Count("name")).get("name__count")
    return restful.ok(message="操作成功",data=data)


@api_view(['POST']) # 未完成
def get_tagBlog(request):
    name = request.data.get("name")
    max_count = request.data.get("maxCount")
    void = request.data.get("void")
    if name and max_count:
        try:
            tag = ArticleCategory.objects.get(name=name)
        except:
            return restful.fail(message="标签不存在")
        articles = Article.objects.filter(category=tag).all()
        serializer = Tag_Blog_Serializer(articles,many=True)
        data = {}
        if void == 1:
            # 随机获得一个热门便签名
            pass
        data["count"] = Article.objects.filter(category=tag).aggregate(Count("author")).get("author__count")
        data["blogs"] = serializer.data

        return restful.ok(message="操作成功",data=data)

    else:
        return restful.fail(message="传入参数错误")














