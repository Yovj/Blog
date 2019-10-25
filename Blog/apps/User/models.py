from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from shortuuidfield import  ShortUUIDField

class UserManager(BaseUserManager):
    def _create_user(self,telephone,username,password,**kwargs):
        if not telephone:
            raise ValueError("请传入手机号码")
        if not username:
            raise ValueError("请传入用户名")
        if not password:
            raise ValueError("密码")

        user = self.model(telephone=telephone,username=username,**kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_user(self,telephone,username,password,**kwargs):
        kwargs['is_superuser'] = False
        return self._create_user(telephone,username,password,**kwargs)

    def create_superuser(self,telephone,username,password,**kwargs):
        kwargs['is_superuser'] = True
        kwargs['is_staff'] = True
        return self._create_user(telephone,username,password,**kwargs)


class User(AbstractBaseUser,PermissionsMixin):
    uid = ShortUUIDField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True,null=True)
    telephone = models.CharField(max_length=11,unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    data_joined = models.DateTimeField(auto_now_add=True)
    data_modify = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=100)
    sex = models.BooleanField(default=True)
    avatar = models.CharField(max_length=100,default='/')
    birth_time = models.DateTimeField(auto_now_add=True)


    USERNAME_FIELD = 'telephone'
    # telephone，username，password
    REQUIRED_FIELDS = ['username']
    EMAIL_FIELD = 'email'

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username





