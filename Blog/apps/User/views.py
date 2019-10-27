from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .serializers import LoginSerializer
from django.contrib.auth import login,logout,authenticate
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from utils import restful
from .models import User,Relation_Detail,Like_Detail
from .serializers import LoginSerializer,LoginReturnSerializer
from .serializers import RegisterSerializer,UpdateSerializer,UserSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from .serializers import ListUserReturnSerializer
from apps.article.models import Article,Comment
from django.db.models import Count
from apps.article.serializer import CommentSerializer

# 判断博文是否存在，如果是，返回对象






@api_view(['POST'])
def register_View(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        username = serializer.data.get("name")
        password = serializer.data.get("password")
        email = serializer.data.get("email")
        user = User.objects.create_user(email=email,username=username,password=password)
        login(request,user)
        return restful.ok(message="注册成功")
    else:
        print(serializer.errors)
        return restful.fail(message=serializer.errors)

class update_View(APIView):

    def post(self,request):
        print(request.data)
        serializer = UpdateSerializer(data=request.data)

        if serializer.is_valid():
            print(serializer.data)
            pk = serializer.data.get("id")
            print(type(pk))
            name = serializer.data.get("name")
            email = serializer.data.get("email")
            avatar = serializer.data.get("avatar")
            password = serializer.data.get("password")
            try:
                tag = 0
                user = User.objects.get(pk=pk)
                if user:
                    if name:
                        user.username = name
                        tag = 1
                    if email:
                        user.email = email
                        tag = 1
                    if avatar:
                        user.avatar = avatar
                        tag = 1
                    if password:
                        user.set_password(password)
                        tag = 1
                if tag == 0 :
                    return restful.fail(message="未传入任何需要修改的信息")
                user.save()
                return restful.ok(message="修改成功")
            except:
                return restful.fail(message="用户不存在")
        else:
            if serializer.errors.get("email"):
                return restful.fail(message="邮箱格式错误或已被注册")
            return restful.fail(message="传入参数格式有误")

@api_view(['POST'])
def change_Password(request):
    email = request.data.get("email")
    if email:
        user = User.objects.filter(email=email).first()
        if user:
            return restful.ok(message="邮箱存在")
        else:
            return restful.fail(message="用户不存在")
    else:
        return restful.fail(message="请传入emaill")


@api_view(['POST'])
@csrf_exempt
def login_View(request):
    data = request.data
    serializer = LoginSerializer(data=data)
    if serializer.is_valid():
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request,username=email,password=password)
        if user:
            if user.is_active:
                return_serializer = LoginReturnSerializer(user)
                data = return_serializer.data
                data.update({"name":data.pop("username")})
                print(data)
                login(request,user)
                return restful.ok(data=data,message="")
            else:
                return restful.fail(message="用户已被限制登录")
        else:
            return restful.fail(message="账号或密码错误")
    else:
        print(serializer.errors)
        return restful.fail(message="输入信息格式不符")

@api_view(['POST','GET'])
def for_test(request):
    create_user1 = User.objects.create_user(telephone="18621853521",username="徐逸凡x",password="xuyifan123",email="6140adsad36@qq.com")
    create_user2 = User.objects.create_user(telephone="18621433521",username="徐逸凡y",password="xuyifan123",email="614sadsaw336@qq.com")
    user = User.objects.all()
    relation_detail = Relation_Detail.objects.create(who_relation=create_user1,relation_who=create_user2,relation_type=1)
    serializer = LoginReturnSerializer(user,many=True)
    return Response(serializer.data)


@api_view(['POST'])
def get_user_Detail(request):

    id = request.data.get("id")
    now_id = request.data.get("nowUser")
    try:
        user = User.objects.get(pk=id)
        now_user = User.objects.get(pk=now_id)
    except:
        return restful.fail(message="用户不存在")

    blog_count = user.article_set.all().count()
    follow_count = Relation_Detail.objects.filter(relation_who=user,relation_type=1).all().count()
    serializer = UserSerializer(user)
    data = serializer.data
    data["blogCount"] = blog_count
    data["focusCount"] = follow_count
    if id != now_id:
        is_focus = Relation_Detail.objects.filter(relation_who=user,who_relation=now_user,relation_type=1).first()
        if is_focus:
            data["isFocused"] = 1
        else:
            data["isFocused"] = 0
    return restful.ok(message="操作成功",data=data)


@api_view(['POST'])
def user_Operation(request):
    data = request.data
    id = data.get("id")
    target_id = data.get("target_id")
    operation_type = data.get("type")
    if id and target_id:
        if id == target_id:
            return restful.fail(message="id == targetid ,操作失败")
        if operation_type not in Relation_Detail.RELATION_CHOICES:
            return restful.fail(message="错误的操作类型")
        try:
            user = User.objects.get(pk=id)
            target_user = User.objects.get(pk=target_id)
            relation_detail = Relation_Detail.objects.filter(who_relation=user,relation_who=target_user).first()
            if not relation_detail:
                relation_detail = Relation_Detail.objects.create(who_relation=user,relation_who=target_user,relation_type=operation_type)
                return restful.ok(message="修改成功")
            relation_detail.relation_type = operation_type
            relation_detail.save()
            return restful.ok(message="修改成功")
        except:
            return restful.fail(message="用户不存在")
    else:
        return restful.fail(message="传入参数错误")


@api_view(['POST']) # 未考虑page
def get_FocusList(request):
    id = request.data.get("id")
    pagenum = request.data.get("pagenum")
    pagesize = request.data.get("pagesize")
    orderType = request.data.get("orderType")

    if id and pagenum and pagesize:
        try:
            user = User.objects.get(pk=id)
        except:
            return restful.fail(message="用户不存在")

        focused_user = Relation_Detail.objects.filter(who_relation=user,relation_type=1).all()
        if orderType == 0 :
            focused_user = focused_user.order_by("-who_relation__article__pub_time")
        elif orderType == 1:
            focused_user = focused_user.order_by("-date_relation")
        else:
            return restful.fail("没有指定的排序类型")

        serializer = ListUserReturnSerializer(focused_user,many=True)
        data = serializer.data
        for dict_item in data:
            dict_item['time'] = dict_item.pop("date_relation")
            dict_pop = dict_item.pop("relation_who")
            dict_item["name"] = dict_pop["username"]
            dict_item["avatar"] = dict_pop["avatar"]
            dict_item["id"] = dict_pop["id"]
        return restful.ok(message="成功",data=data)


    else:
        return restful.fail(message="传入参数错误")


@api_view(['POST']) # 未考虑page
def get_BlackList(request):
    id = request.data.get("id")
    pagenum = request.data.get("pagenum")
    pagesize = request.data.get("pagesize")

    if id and pagenum and pagesize:
        try:
            user = User.objects.get(pk=id)
        except:
            return restful.fail(message="用户不存在")


        blacked_user = Relation_Detail.objects.filter(who_relation=user,relation_type=-1).all()
        print(blacked_user)
        serializer = ListUserReturnSerializer(blacked_user,many=True)
        print(serializer.data)
        data = serializer.data
        for dict_item in data:
            dict_item['time'] = dict_item.pop("date_relation")
            dict_pop = dict_item.pop("relation_who")
            dict_item["name"] = dict_pop["username"]
            dict_item["avatar"] = dict_pop["avatar"]
            dict_item["id"] = dict_pop["id"]
        return restful.ok(message="成功",data=data)


    else:
        return restful.fail(message="传入参数错误") # 未考虑page


@api_view(['POST'])
def like_Blog(request):
    data = request.data
    blog_id = data.get("blog_id")
    user_id = data.get("user_id")
    love = data.get("love")
    if blog_id and user_id:
        try:
            user = User.objects.get(pk=user_id)
        except:
            return restful.fail(message="用户不存在")

        try:
                blog = Article.objects.get(pk=blog_id)
        except:
                return restful.fail(message="博文不存在")

        # 对博文进行操作
        if blog.author == user:
            return restful.fail(message="不能对自己的博文操作")
        if love == 0:
            like_detail = Like_Detail.objects.filter(user=user,article=blog).first()
            if not like_detail:
                return restful.fail(message="用户未对博文点赞，不能取消")
            like_detail.delete()
            return restful.ok(message="取消点赞成功")
        elif love == 1:
            # 点赞
            if blog in user.like.all():
                return restful.fail(message="不能重复点赞")
            like_detail = Like_Detail.objects.create(user=user,article=blog)
            return restful.ok(message="点赞成功")
        else:
            return restful.fail(message="操作类型错误")
    else:
        return restful.fail(message="请传入博文id")


@api_view(['POST'])
def comment_Blog(request):
    data = request.data
    blog_id = data.get("id")
    user_id = data.get("user_id")
    to_user_id = data.get("to_user_id")
    text = data.get("text")
    try:
        blog = Article.objects.get(pk=blog_id)
    except:
        return restful.fail(message="博文不存在")

    try:
        to_user = User.objects.get(pk=to_user_id)
        user = User.objects.get(pk=user_id)
    except:
        return restful.fail(message="用户不存在")
    blacked_users = Relation_Detail.objects.filter(who_relation=to_user,relation_type=-1).all()
    for blacked_user in blacked_users.all():
        if user == blacked_user.relation_who:
            return restful.fail(message="被拉黑用户不能评论")

    comment = Comment.objects.create(content=text,article=blog,author=user)
    return restful.ok(message="评论成功")

@api_view(['POST']) # 未考虑page
def get_commentList(request):
    id = request.data.get("id") # 博文id
    pagenum = request.data.get("pagenum")
    pagesize = request.data.get("pagesize")
    try:
        blog = Article.objects.get(pk=id)
    except:
        return restful.fail(message="博文不存在")

    comments = blog.comments.all()
    serializer = CommentSerializer(comments,many=True)
    data = serializer.data
    for dict_item in data:
        dict_item["to_user"] = dict_item.pop("article").pop("author")
        dict_item["user"] = dict_item.pop("author")
    print(data)
    return restful.ok(message="操作成功",data=data) # 未考虑page



@api_view(['POST']) # 未完成 # 未考虑page
def search_User(request):
    id = request.data.get("id") # 用户id
    pagenum = request.data.get("pagenum")
    pagesize = request.data.get("pagesize")
    key_word = request.data.get("search")

    try:
        user = User.objects.get(pk=id)
    except:
        return restful.fail(message="用户不存在")


