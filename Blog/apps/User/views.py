from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .serializers import LoginSerializer
from django.contrib.auth import login,logout,authenticate
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from utils import restful
from .models import User,Relation_Detail,Like_Detail,Recommand_Detail
from .serializers import LoginSerializer,LoginReturnSerializer,Relation_Time_Serializer
from .serializers import RegisterSerializer,UpdateSerializer,UserSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from .serializers import ListUserReturnSerializer
from apps.article.models import Article,Comment
from django.db.models import Count
from apps.article.serializer import CommentSerializer
from apps.article.serializer import Return_User_Serializer
from django.db.models import Q
from .serializers import RecommendList_Serializer
import collections
import logging

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

@api_view(['POST'])
def update_View(request):
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


# class update_View(APIView):
#
#     def post(self,request):
#         print(request.data)
#         serializer = UpdateSerializer(data=request.data)
#
#         if serializer.is_valid():
#             print(serializer.data)
#             pk = serializer.data.get("id")
#             print(type(pk))
#             name = serializer.data.get("name")
#             email = serializer.data.get("email")
#             avatar = serializer.data.get("avatar")
#             password = serializer.data.get("password")
#             try:
#                 tag = 0
#                 user = User.objects.get(pk=pk)
#                 if user:
#                     if name:
#                         user.username = name
#                         tag = 1
#                     if email:
#                         user.email = email
#                         tag = 1
#                     if avatar:
#                         user.avatar = avatar
#                         tag = 1
#                     if password:
#                         user.set_password(password)
#                         tag = 1
#                 if tag == 0 :
#                     return restful.fail(message="未传入任何需要修改的信息")
#                 user.save()
#                 return restful.ok(message="修改成功")
#             except:
#                 return restful.fail(message="用户不存在")
#         else:
#             if serializer.errors.get("email"):
#                 return restful.fail(message="邮箱格式错误或已被注册")
#             return restful.fail(message="传入参数格式有误")

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
            if relation_detail.relation_type == 0:
                relation_detail.delete()
            return restful.ok(message="修改成功")
        except:
            return restful.fail(message="用户不存在")
    else:
        logger = logging.getLogger('stu')
        logger.info('url:%s method:%s 成功'% (request.path, request.method))
        return restful.fail(message="传入参数错误")


@api_view(['POST']) # 未考虑search
def get_FocusList(request):
    id = request.data.get("id")
    pagenum = request.data.get("pagenum")
    pagesize = request.data.get("pagesize")
    orderType = request.data.get("orderType")
    search = request.data.get('search')

    if id and pagenum and pagesize:
        try:
            user = User.objects.get(pk=id)
        except:
            return restful.fail(message="用户不存在")

        focused_user = Relation_Detail.objects.filter(Q(who_relation=user) & (Q(relation_type=1) | Q(relation_type=2))  & Q(relation_who__username__icontains=search)).all()
        print(focused_user)
        if orderType == 0 :

            focused_user = focused_user[(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]
            print(focused_user)
        elif orderType == 1:
            focused_user = focused_user.order_by("-date_relation").all()[(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]
        else:
            return restful.fail("没有指定的排序类型")

        serializer = ListUserReturnSerializer(focused_user,many=True)
        data = {}
        data['users'] = serializer.data
        data['total'] = focused_user.count()
        for dict_item in data['users']:
            dict_item['time'] = dict_item.pop("date_relation")
            dict_pop = dict_item.pop("relation_who")
            dict_item["name"] = dict_pop["username"]
            dict_item["avatar"] = dict_pop["avatar"]
            dict_item["id"] = dict_pop["id"]
        return restful.ok(message="成功",data=data)


    else:
        return restful.fail(message="传入参数错误")


@api_view(['POST'])
def get_BlackList(request):
    id = request.data.get("id")
    pagenum = request.data.get("pagenum")
    pagesize = request.data.get("pagesize")

    if id and pagenum and pagesize:
        try:
            user = User.objects.get(pk=id)
        except:
            return restful.fail(message="用户不存在")


        blacked_user = Relation_Detail.objects.filter(who_relation=user,relation_type=-1).all()[(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]
        print(blacked_user)
        serializer = ListUserReturnSerializer(blacked_user,many=True)
        print(serializer.data)
        data = {}
        data['users'] = serializer.data
        for dict_item in data['users']:
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
            blog.like_count -= 1
            blog.save()
            like_detail.delete()
            return restful.ok(message="取消点赞成功")
        elif love == 1:
            # 点赞
            if blog in user.like.all():
                return restful.fail(message="不能重复点赞")
            like_detail = Like_Detail.objects.create(user=user,article=blog)
            blog.like_count += 1
            blog.save()
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

    comment = Comment.objects.create(content=text,article=blog,author=user,to_user=to_user.id)
    comment_count = blog.comment_count
    blog.comment_count = comment_count + 1
    blog.save()

    return restful.ok(message="评论成功")

@api_view(['POST'])
def get_commentList(request):
    id = request.data.get("id") # 博文id
    pagenum = request.data.get("pagenum")
    pagesize = request.data.get("pagesize")
    try:
        blog = Article.objects.get(pk=id)
    except:
        return restful.fail(message="博文不存在")

    comments = blog.comments.all().order_by('pub_time')[(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]
    serializer = CommentSerializer(comments,many=True)
    data = serializer.data
    to_user = []
    index = 0
    count = comments.count()
    for index in range(0,count):
        to_user.append(comments[index].to_user)
        print(comments[index].to_user)
    index = 0
    for dict_item in data:
        dict_item.pop("article").pop("author")
        user_item = User.objects.get(pk=to_user[index])
        dict_item["to_user"] = {}
        dict_item["to_user"]["id"] = user_item.id
        dict_item["to_user"]["name"] = user_item.username
        index += 1
        dict_item["user"] = dict_item.pop("author")
    print(data)
    for data_item in data:
        data_item['user']['name'] = data_item['user'].pop('username')

    return_data = {}
    return_data['list'] = data
    return restful.ok(message="操作成功",data=return_data)



@api_view(['POST'])
def search_User(request):
    id = request.data.get("id") # 用户id
    pagenum = request.data.get("pagenum")
    pagesize = request.data.get("pagesize")
    key_word = request.data.get("search")
    if id and key_word:
        try:
            user = User.objects.get(pk=id)
        except:
            return restful.fail(message="用户不存在")

        blacked_user = Relation_Detail.objects.filter(who_relation=user,relation_type=-1).all()
        blacked_id = []
        for blacked_user_item in blacked_user:
            blacked_id.append(blacked_user_item.relation_who.id)
        # print(blacked_id)
        # 查询出来的用户
        users_all = User.objects.filter(Q(username__icontains=key_word) & ~Q(id=id)).exclude(id__in=blacked_id).all()
        users = users_all[(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]
        total = users_all.count()
        serializer = Relation_Time_Serializer(users,many=True)
        data = serializer.data
        return_data = {}
        return_data["total"] = total
        for dict_item in data:
            id_dict = dict_item["id"]
            last_article = Article.objects.filter(author__id=id_dict).all()
            if last_article:
                pub_time = last_article.order_by('-pub_time').first().pub_time
                dict_item["time"] = pub_time
            else:
                print("None error for test")
                dict_item["time"] = None

            is_focus = Relation_Detail.objects.filter(who_relation=user,relation_who__id=id_dict,relation_type=1).first()
            if is_focus:
                dict_item["isFocused"] = 1
            else:
                dict_item["isFocused"] = 0
        return_data["users"] = data
        return restful.ok(message="操作成功",data=return_data)
    else:
        return restful.fail(message="传入参数错误")




@api_view(['POST'])
def recommend_Blog(request):
    blog_id = request.data.get("blog_id")
    user_id = request.data.get("user_id")
    operation_type = request.data.get("recommend")
    if blog_id and user_id:
        try:
            user = User.objects.get(pk=user_id)
            blog = Article.objects.get(pk=blog_id)
        except:
            return restful.fail(message="用户或博文不存在")
        is_exist = Recommand_Detail.objects.filter(user=user,article=blog).first()
        if operation_type == 0:
            # 取消推荐
            if not is_exist:
                return restful.fail(message="用户尚未推荐该博文")
            is_exist.delete()
            return restful.ok(message="取消推荐成功")
        elif operation_type == 1:
            # 推荐
            if is_exist:
                return restful.fail(message="不能重复推荐")
            recommand_detail = Recommand_Detail.objects.create(user=user,article=blog)
            return restful.ok(message="推荐成功")
        else:
            return restful.fail(message="错误的操作类型")
    else:
        return restful.fail(message="传入参数错误")


@api_view(['POST']) # page
def get_hostList(request):
    id = request.data.get("id") # 博文id
    pagenum = request.data.get("pagenum")
    pagesize = request.data.get("pagesize")

    if id:
        try:
            blog = Article.objects.get(pk=id)
        except:
            return restful.fail(message="博文不存在")

        like_users = User.objects.filter(like_detail__article=blog).all()
        serializer = Return_User_Serializer(like_users,many=True)
        data_like = serializer.data.copy()


        for data_item in data_like:
            data_item['type'] = 0
        recommend_users = User.objects.filter(recommand_detail__article=blog).all()[(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]
        serializer_recommend = Return_User_Serializer(recommend_users,many=True)
        data_recommend = serializer_recommend.data.copy()
        for data_item in data_recommend:
            data_item['type'] = 1

        print(data_recommend)
        print(data_like)
        data = data_like + data_recommend
        for data_item in data:
            data_item['name'] = data_item.pop("username")
        return_data = {}
        return_data['list'] = data
        return restful.ok(message="操作成功",data=return_data)


    else:
        return restful.fail(message="传入参数错误")



@api_view(['POST'])
def get_recommend_list(request):
    id = request.data.get("id") # 用户id
    pagenum = request.data.get("pagenum")
    pagesize = request.data.get("pagesize")

    try:
        user = User.objects.get(pk=id)
    except:
        return restful.fail(message="用户不存在")
    # 当前用户关注的
    focus_user = User.objects.filter(Q(relation_who_set__relation_type=1) & Q(relation_who_set__who_relation=user))
    hate_user = User.objects.filter(relation_who_set__who_relation=user,relation_who_set__relation_type=-1)
    hate_user_id = []
    for user_item in hate_user:
        hate_user_id.append(user_item.id)
    hate_user_id.append(id)

    recommend_user = User.objects.filter(Q(relation_who_set__relation_type=1) & Q(relation_who_set__who_relation__in=focus_user) & ~Q(id__in=hate_user_id))

    if len(recommend_user) == 0:
        recommend_user = User.objects.filter(~Q(id__in=hate_user)).all()



    user_recommend_id = []
    for recommend_item in recommend_user:
        user_recommend_id.append(recommend_item.id)
    recommend_user = User.objects.filter(~Q(id=id) & Q(id__in=user_recommend_id) ).order_by('?')[(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]
    total = recommend_user.count()
    #print("recommend_user.count:",recommend_user.count())
    recommend_list_serializer = RecommendList_Serializer(recommend_user,many=True)
    data = recommend_list_serializer.data
    #print("data:",data)
    return_data = {}
    return_data['total'] = total
    for user_item in data:
        data_tags = {}
        user_item['name'] = user_item.pop("username")
        for data_item in user_item.get("article_set"):
            data_tags = data_item.pop("category")
        user_item["tags"] = data_tags
        if user_item["tags"] and len(user_item["tags"]) > 5:
            user_item["tags"] = user_item["tags"][0:5]

        user_item["blogs"] = user_item.pop("article_set")
        if user_item["blogs"] and len(user_item["blogs"]) > 4:
            user_item["blogs"] = user_item["blogs"][0:1]
        tag_name = []
        for tag in user_item['tags']:
            tag_name.append(tag['name'])
        user_item['tags'] = tag_name
    return_data['users'] = data
    return restful.ok(message="操作成功",data=return_data)


# [(pagenum- 1) * pagesize : (pagenum- 1) * pagesize + pagesize]