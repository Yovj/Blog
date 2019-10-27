from django.db import models
from utils import restful
import datetime
# Create your models here.

class ArticleCategory(models.Model):
    name = models.CharField(max_length=100,unique=True)
    count = models.IntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True)
    is_great = models.BooleanField(default=0)


class Article(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    pub_time = models.DateTimeField(auto_now_add=True)
    thumbnail = models.URLField(null=True)
    category = models.ManyToManyField('ArticleCategory',related_name='articles')
    author = models.ForeignKey('user.User',on_delete=models.CASCADE)
    is_great = models.BooleanField(default=0)
    # 点赞数和评论数 ...
    class Meta:
        ordering = ['-pub_time']

class Comment(models.Model):
    content = models.TextField()
    pub_time = models.DateTimeField(auto_now_add=True)
    article = models.ForeignKey('Article',on_delete=models.CASCADE,related_name='comments')
    author = models.ForeignKey('user.User',on_delete=models.CASCADE)
    # 外键引用自身，注意添加

    class Meta:
        ordering = ['-pub_time']

    def __str__(self):
        return "<article:(id:%s,title:%s)>" % (self.id,self.title)
