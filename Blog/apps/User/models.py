from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from shortuuidfield import  ShortUUIDField

class UserManager(BaseUserManager):
    def _create_user(self,email,username,password,**kwargs):
        if not email:
            raise ValueError("请传入手机号码")
        if not username:
            raise ValueError("请传入用户名")
        if not password:
            raise ValueError("密码")

        user = self.model(email=email,username=username,**kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_user(self,email,username,password,**kwargs):
        kwargs['is_superuser'] = False
        return self._create_user(email,username,password,**kwargs)

    def create_superuser(self,email,username,password,**kwargs):
        kwargs['is_superuser'] = True
        kwargs['is_staff'] = True
        return self._create_user(email,username,password,**kwargs)


class User(AbstractBaseUser,PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True,null=True)
    telephone = models.CharField(max_length=11)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    data_joined = models.DateTimeField(auto_now_add=True)
    data_modify = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=100)
    sex = models.BooleanField(default=True)
    avatar = models.CharField(max_length=100,default='/')
    birth_time = models.DateTimeField(auto_now_add=True)
    relation = models.ManyToManyField('self',through="Relation_Detail",symmetrical=False)
    like = models.ManyToManyField('article.Article',related_name="like_set",through="Like_Detail")
    recommend = models.ManyToManyField('article.Article',related_name="recommend_set",through="Recommand_Detail")


    USERNAME_FIELD = 'email'
    # telephone，username，password
    REQUIRED_FIELDS = ['username']
    EMAIL_FIELD = 'email'
    objects = UserManager()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

class Relation_Detail(models.Model):
    RELATION_CHOICES = [-1,0,1,2]
    who_relation = models.ForeignKey(User,on_delete=models.CASCADE,related_name="who_relation_set")
    relation_who = models.ForeignKey(User,on_delete=models.CASCADE,related_name="relation_who_set")
    date_relation = models.DateTimeField(auto_now_add=True)
    relation_type = models.IntegerField(default=0)


class Like_Detail(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    article = models.ForeignKey('article.Article',on_delete=models.CASCADE)
    date_like = models.DateTimeField(auto_now_add=True)

class Recommand_Detail(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    article = models.ForeignKey('article.Article',on_delete=models.CASCADE)
    date_recommand = models.DateTimeField(auto_now_add=True)





