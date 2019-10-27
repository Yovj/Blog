"""Blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from apps.article import views


urlpatterns = [
    path('', include('apps.user.urls')),
    path('blog/',include('apps.article.urls')),
    path('tag/view/',views.vist_tag),
    path("tag/user_list/",views.get_tag_UerList),
    path("tag/list/",views.get_tagList),
    path("tag/card_info/",views.get_tagBlog)
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT) # 记得在URL中更改os.path
