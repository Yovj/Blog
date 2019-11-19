from django.shortcuts import render
from django.views.decorators.http import require_POST
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .serializer import PublishSerializer,TagSerializer
from utils import restful
from apps.user.models import User,Relation_Detail
from .models import Article,ArticleCategory,Comment
from .serializer import Return_User_Serializer,Tag_Blog_Serializer,Blog_Detail_Serializer
from django.db.models import Q,Count
from apps.user.models import Like_Detail,Recommand_Detail
from .serializer import CommentList_Serializer,CommentList_Author_Serializer,HotList_Serializer
from .serializer import BlogDetail_Serializer,BlogDetail_Recommend_User_Serializer,BlogDetail_OwnBlog_Serializer
from .mysql_host_view import hot_Info_View
from django.db import connection
import collections
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
            data['tags'] = [tags_dict]
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
                data['tags'] = [tags_dict]
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
            data = {}
            data['count'] = 0
            return restful.ok(data=data)
        tag.count += 1
        tag.save()
        data = {}
        data['count'] = tag.count
        return restful.ok(message="访问成功",data=data)
    else:
        return restful.fail(message="请传入标签名称")


@api_view(['POST'])
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
            data = {}
            data['users'] = []
            return restful.ok(message="用户或便签不存在",data=data)


        related_users = User.objects.filter(Q(article__category=tag) & ~Q(id=id)).all()[(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]
        serializer = Return_User_Serializer(related_users,many=True)
        #focused_user = Relation_Detail.objects.filter(who_relation=user,relation_type=1).all()
        data = serializer.data
        for dict_item in data:
            id_dict = dict_item["id"]
            is_focus = Relation_Detail.objects.filter(who_relation=user,relation_who__id=id_dict,relation_type=1).first()
            if is_focus:
                dict_item["isFocused"] = 1
            else:
                dict_item["isFocused"] = 0
        return_data = {}
        return_data['users'] = data
        return restful.ok(message="成功",data=return_data)
    else:
        return restful.fail(message="传入参数错误")


@api_view(['POST'])
def get_tagList(request):
    pagenum = request.data.get("pagenum")
    pagesize = request.data.get("pagesize")
    type_operation = request.data.get("type")

    if type_operation == 0: # 热门
        tags = ArticleCategory.objects.all().order_by("count")[(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]
        serializer = TagSerializer(tags,many=True)

    elif type_operation == 1: # 最新
        tags = ArticleCategory.objects.all().order_by("-time")[(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]
        serializer = TagSerializer(tags,many=True)
    else:
        return restful.fail(message="传入参数错误")
    data = {}
    data["tags"] = []
    for tag_item in serializer.data:
        data["tags"].append(tag_item["name"])
    data["total"] = ArticleCategory.objects.aggregate(Count("name")).get("name__count")
    return restful.ok(message="操作成功",data=data)


@api_view(['POST'])
def get_tagBlog(request):
    name = request.data.get("name")
    max_count = request.data.get("maxCount")
    void = request.data.get("void")
    if name and max_count:
        try:
            tag = ArticleCategory.objects.get(name=name)
        except:
            if void == 1:
                new_tag = ArticleCategory.objects.filter(~Q(name = name)).order_by("count").first()
                if not new_tag:
                    return restful.fail(message="无便签可推荐")
                dataa = {}
                dataa["name"] = new_tag.name
                dataa["count"] = Article.objects.filter(category=new_tag).aggregate(Count("author")).get("author__count")

                articles = Article.objects.filter(category=new_tag).order_by("like_count","comment_count")

                count = len(articles)
                if count > max_count:
                    count = max_count
                serializer = Tag_Blog_Serializer(articles[0:count],many=True)
                data_blog = serializer.data
                for data_blog_item in data_blog:
                    data_blog_item['userId'] = data_blog_item.pop("author")
                    data_blog_item["pic"] = data_blog_item.pop("thumbnail")
                dataa["blogs"] = data_blog

                return restful.ok(message="操作成功",data=dataa)
            else:
                dataa = {}
                dataa["name"] = []
                dataa["count"] = 0
                dataa["blogs"] = []
                return restful.ok(message="操作成功",data=dataa)
        articles = Article.objects.filter(category=tag).order_by("like_count","comment_count")
        count = len(articles)
        if count > max_count:
            count = max_count
        serializer = Tag_Blog_Serializer(articles[0:count],many=True)
        data = {}
        if void == 1:
            new_tag = ArticleCategory.objects.filter(~Q(name = name)).order_by("count").first()
            if not new_tag:
                return restful.fail(message="无便签可推荐")
            data["name"] = new_tag.name
            tag = ArticleCategory.objects.get(name=new_tag.name)

        data["count"] = Article.objects.filter(category=tag).aggregate(Count("author")).get("author__count")
        print(data["count"])
        print(Article.objects.filter(category=tag).aggregate(Count("author")))
        data_blog = serializer.data
        for data_blog_item in data_blog:
            data_blog_item['userId'] = data_blog_item.pop("author")
            data_blog_item["pic"] = data_blog_item.pop("thumbnail")
        data["blogs"] = data_blog

        return restful.ok(message="操作成功",data=data)

    else:
        return restful.fail(message="传入参数错误")



@api_view(['POST']) # 未完成
def get_blogDetail(request):
    id = request.data.get('id') # 博文id
    user_id = request.data.get('user_id') # 当前用户id
    commentSize = request.data.get('commentSize') # 评论最大数量
    hotSize = request.data.get('hotSize')
    if not commentSize or not hotSize:
        return restful.fail(message="传入参数不足")

    try:
        blog = Article.objects.get(pk=id)
        user = User.objects.get(pk=user_id)
    except:
        return restful.fail(message="用户或博文不存在")

    serializer = Blog_Detail_Serializer(blog)
    blog_data = {}
    blog_data['blog'] = serializer.data
    blog_data['blog']["time"] = blog_data['blog'].pop("pub_time")
    blog_data['blog']["pics"] = []
    blog_data['blog']["pics"].append(blog_data['blog'].pop("thumbnail"))
    blog_data['blog']["tags"] = blog_data['blog'].pop("category")
    is_loved = Like_Detail.objects.filter(user=user,article=blog).first()
    if is_loved:
        blog_data['blog']["isLoved"] = True
    else:
        blog_data['blog']["isLoved"] = False
    is_Referred = Recommand_Detail.objects.filter(user=user,article=blog).first()
    if is_Referred:
        blog_data['blog']["isReferred"] = True
    else:
        blog_data['blog']["isReferred"] = False
    comment_count = Comment.objects.filter(article=blog).all().count()
    blog_data['blog']['commentCount'] = comment_count

    # commentList部分
    blog_comment = Comment.objects.filter(article=blog).all()
    # print(blog_comment.count())
    if blog_comment.count() >= commentSize:
        blog_comment = blog_comment[0:commentSize]
    comment_serializer = CommentList_Serializer(blog_comment,many=True)
    comment_data = comment_serializer.data
    for comment_data_item in comment_data:
        comment_data_item["text"] = comment_data_item.pop("content")
        comment_data_item["user"] = comment_data_item.pop("author")
        comment_data_item["user"]['name'] = comment_data_item["user"].pop('username')
        comment_data_item["to_user"] = comment_data_item.pop("article").pop("author")
        comment_data_item["to_user"]['name'] = comment_data_item["to_user"].pop('username')
    blog_data["commentList"] = comment_data

    # hotList 部分 未完成
    like_count = Like_Detail.objects.filter(article=blog).all().count()
    recommend_count = Recommand_Detail.objects.filter(article=blog).all().count()
    blog_data['blog']['hotCount'] = like_count+recommend_count # 未完成，待修改
    # user_like = User.objects.filter(like_detail__article=blog).all()
    # user_recommend = User.objects.filter(recommand_detail__article=blog).all()
    # print(user_like)
    # print(user_recommend)
    cursor = connection.cursor()
    cursor.execute("select * from(select date_recommand time,article_id,user_id,1 as type from user_recommand_detail union select date_like time,article_id,user_id,0 as type from user_like_detail) tab order by time desc")
    rows = cursor.fetchall()
    hot_dict = []
    for row in rows:
        if row[1] != id:
            continue
        hot_user = User.objects.get(pk=row[2])
        serializer_hot = HotList_Serializer(hot_user)
        hot_data = serializer_hot.data
        hot_data['type'] = row[3]
        hot_data['name'] = hot_data.pop('username')
        hot_dict.append(hot_data)
        print(row)
    if len(hot_dict) >= hotSize:
        hot_dict = hot_dict[0:hotSize]
    blog_data['hotList'] = hot_dict



    return restful.ok(message="操作成功",data=blog_data)


@api_view(['POST']) # 未完成 # 此处有问题!!!!
def get_blogList(request):
    id = request.data.get("id")
    isHome = request.data.get("isHome")
    pagenum = request.data.get('pagenum')
    pagesize = request.data.get("pagesize")

    try:
        user = User.objects.get(pk=id)
    except:
        return restful.fail(message="用户不存在")

    if isHome == True: # 需要该用户的博文和关注用户发表和推荐的博文
        focused_user = User.objects.filter(relation_who_set__relation_type=1,relation_who_set__who_relation=user)
        print(focused_user)
        focused_user_blog = Article.objects.filter( ~Q(author=user) & (Q(author__in=focused_user) | Q(recommand_detail__user__in=focused_user))).all().order_by("-pub_time")
        # print(focused_user_blog.query)
        print(focused_user_blog)
        user_blog = Article.objects.filter(author=user).all().order_by("-pub_time") # 该用户的博文
        serializer = BlogDetail_Serializer(focused_user_blog,many=True)
        blog_data = serializer.data
        index = 0
        # 关注用户发表和推荐的博文

        for blog_data_item in blog_data:
            blog_data_item["time"] = blog_data_item.pop("pub_time")
            blog_data_item["pic"] = blog_data_item.pop("thumbnail")
            blog_data_item['tags'] = blog_data_item.pop("category")
            for tag_item in blog_data_item['tags']:
                tag_item["isHot"] = tag_item.pop("is_great")
            blog_data_item["user"] = blog_data_item.pop("author")
            blog_data_item["user"]["name"] = blog_data_item["user"].pop("username")
            blog_temp = focused_user_blog[index]
            focused_user_item = focused_user.filter(recommand_detail__article=blog_temp).first()
            recommend_user_serializer = BlogDetail_Recommend_User_Serializer(focused_user_item)
            blog_data_item["referrer"] = recommend_user_serializer.data
            blog_data_item["referrer"]["name"] = blog_data_item["referrer"].pop("username")
            blog_data_item["commentCount"] = blog_data_item.pop("comment_count")

            blog_data_item["picCount"] = 0 # 此处有问题!!!!
            blog_temp = focused_user_blog[index]
            blog_data_item["hotCount"] = blog_temp.like_count + Recommand_Detail.objects.filter(article=blog_temp).count()
            isLoved = Like_Detail.objects.filter(user=user,article=blog_temp).first()
            if isLoved:
                blog_data_item["isLoved"] = 1
            else:
                blog_data_item["isLoved"] = 0

            isReferred = Recommand_Detail.objects.filter(user=user,article=blog_temp).first()
            if isReferred:
                blog_data_item["isReferred"] = 1
            else:
                blog_data_item["isReferred"] = 0
            index += 1

        #user_blog = Article.objects.filter(author=user).all() # 该用户的博文
        own_serializer = BlogDetail_OwnBlog_Serializer(user_blog,many=True)
        user_blog_data = own_serializer.data

        for blog_data_item in user_blog_data:
            blog_data_item["time"] = blog_data_item.pop("pub_time")
            blog_data_item["pic"] = blog_data_item.pop("thumbnail")
            blog_data_item['tags'] = blog_data_item.pop("category")
            for tag_item in blog_data_item['tags']:
                tag_item["isHot"] = tag_item.pop("is_great")
            blog_data_item["user"] = blog_data_item.pop("author")
            blog_data_item["user"]["name"] = blog_data_item["user"].pop("username")
            blog_data_item["referrer"] = {}
            blog_temp = Article.objects.get(pk=blog_data_item["id"])
            blog_data_item["hotCount"] = Recommand_Detail.objects.filter(article=blog_temp).count() + blog_temp.like_count
            blog_data_item["commentCount"] = blog_data_item.pop("comment_count")
            blog_data_item["picCount"] = 0 # 此处有问题!!!!

        return_data = []
        index_own = 0
        index_focus = 0
        while (index_own < len(blog_data) and index_focus < len(user_blog_data)):
            if blog_data[index_own]["time"] > user_blog_data[index_focus]["time"]:
                return_data.append(blog_data[index_own])
                index_own += 1
            else:
                return_data.append(user_blog_data[index_focus])
                index_focus += 1

        for i in range(index_own,len(blog_data)):
            return_data.append(blog_data[i])

        for i in range(index_focus,len(user_blog_data)):
            return_data.append(user_blog_data[i])



        data = {}
        data['blogs'] = return_data[(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]
        total = len(data['blogs'])
        data['total'] = total

        return restful.ok(message="操作成功",data=data)
    else: #isHome=0 按照user_id和tag来筛选,目标关键词：博文标题或内容中存在的内容
        tagType = request.data.get("tagType")
        search = request.data.get("search")
        user_id = request.data.get("user_id")
        tag = request.data.get("tag")
        if not search:
                    search = ""
        if user_id:
            user = User.objects.get(pk=user_id)
            if tag:
                blogs = Article.objects.filter(Q(author__id=user_id) & Q(category__name=tag) &(Q(text__icontains=search) | Q(title__icontains=search))).all()[(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]
                print(blogs.query)
            else:
                blogs = Article.objects.filter(Q(author__id=user_id)  &(Q(text__icontains=search) | Q(title__icontains=search))).all()[(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]
                print(blogs.query)
            total = blogs.count()
            blogs_serializer = BlogDetail_OwnBlog_Serializer(blogs,many=True)
            blog_data = blogs_serializer.data
            data = {}
            data['total'] = total
            for blog_data_item in blog_data:
                blog_data_item["time"] = blog_data_item.pop("pub_time")
                blog_data_item["pic"] = blog_data_item.pop("thumbnail")
                blog_data_item['tags'] = blog_data_item.pop("category")
                for tag_item in blog_data_item['tags']:
                    tag_item["isHot"] = tag_item.pop("is_great")
                blog_data_item["user"] = blog_data_item.pop("author")
                blog_data_item["user"]["name"] = blog_data_item["user"].pop("username")
                blog_data_item["commentCount"] = blog_data_item.pop("comment_count")

                blog_data_item["picCount"] = 0 # 此处有问题!!!!
                blog_temp = Article.objects.get(pk=blog_data_item["id"])
                blog_data_item["hotCount"] = blog_temp.like_count + Recommand_Detail.objects.filter(article=blog_temp).count()
                if blog_temp.author.id != id:
                    isLoved = Like_Detail.objects.filter(user=user,article=blog_temp).first()
                    if isLoved:
                        blog_data_item["isLoved"] = 1
                    else:
                        blog_data_item["isLoved"] = 0

                    isReferred = Recommand_Detail.objects.filter(user=user,article=blog_temp).first()
                    if isReferred:
                        blog_data_item["isReferred"] = 1
                    else:
                        blog_data_item["isReferred"] = 0
            data['blogs'] = blog_data
            return restful.ok(message="操作成功",data=data)
        else:
            if tag:
                blogs = Article.objects.filter( Q(category__name=tag) &(Q(text__icontains=search) | Q(title__icontains=search))).all()[(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]
                print(blogs.query)
            else:
                blogs = Article.objects.filter((Q(text__icontains=search) | Q(title__icontains=search))).all()[(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]
                print(blogs.query)
            total = blogs.count()
            blogs_serializer = BlogDetail_OwnBlog_Serializer(blogs,many=True)
            blog_data = blogs_serializer.data
            data = {}
            data['total'] = total
            for blog_data_item in blog_data:
                blog_data_item["time"] = blog_data_item.pop("pub_time")
                blog_data_item["pic"] = blog_data_item.pop("thumbnail")
                blog_data_item['tags'] = blog_data_item.pop("category")
                for tag_item in blog_data_item['tags']:
                    tag_item["isHot"] = tag_item.pop("is_great")
                blog_data_item["user"] = blog_data_item.pop("author")
                blog_data_item["user"]["name"] = blog_data_item["user"].pop("username")
                blog_data_item["commentCount"] = blog_data_item.pop("comment_count")

                blog_data_item["picCount"] = 0 # 此处有问题!!!!
                blog_temp = Article.objects.get(pk=blog_data_item["id"])
                blog_data_item["hotCount"] = blog_temp.like_count + Recommand_Detail.objects.filter(article=blog_temp).count()
                if blog_temp.author.id != id:
                    isLoved = Like_Detail.objects.filter(user=user,article=blog_temp).first()
                    if isLoved:
                        blog_data_item["isLoved"] = 1
                    else:
                        blog_data_item["isLoved"] = 0

                    isReferred = Recommand_Detail.objects.filter(user=user,article=blog_temp).first()
                    if isReferred:
                        blog_data_item["isReferred"] = 1
                    else:
                        blog_data_item["isReferred"] = 0
            data['blogs'] = blog_data
            return restful.ok(message="操作成功",data=data)


















