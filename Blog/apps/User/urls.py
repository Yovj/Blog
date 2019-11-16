from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

app_name = 'user'


urlpatterns = [
    path('login/',csrf_exempt(views.login_View)),
    path('test/',views.for_test),
    path('register/',views.register_View),
    path('user/modify/',views.update_View),
    path('send_email/',views.change_Password),
    path('user/info/',views.get_user_Detail),
    path("user_user/change_relation/",views.user_Operation),
    path("user_user/focus_list/",views.get_FocusList),
    path("user_user/black_list/",views.get_BlackList),
    path("user_user/recommend_list/",views.get_recommend_list),
    path("user_blog/love/",views.like_Blog),
    path("user_blog/comment/",views.comment_Blog),
    path('user_blog/comment_list/',views.get_commentList),
    path("user_user/search/",views.search_User),
    path("user_blog/recommend/",views.recommend_Blog),
    path("user_blog/hot_list/",views.get_hostList),


]