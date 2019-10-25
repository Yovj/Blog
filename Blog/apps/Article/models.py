from django.db import models
from apps.User.models import User

# Create your models here.

class ArticleCategory(models.Model):
    name = models.CharField(max_length=100)
    count = models.IntegerField(default=0)


class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    pub_time = models.DateTimeField(auto_now_add=True)
    thumbnail = models.URLField()
    category = models.ManyToManyField('ArticleCategory',on_delete=models.SET_NULL,null=True,related_name='articles')
    author = models.ForeignKey('User',on_delete=models.SET_NULL,null=True)

    class Meta:
        ordering = ['-pub_time']

class Comment(models.Model):
    content = models.TextField()
    pub_time = models.DateTimeField(auto_now_add=True)
    article = models.ForeignKey('Article',on_delete=models.CASCADE,related_name='comments')
    author = models.ForeignKey('User',on_delete=models.CASCADE)

    class Meta:
        ordering = ['-pub_time']




    def __str__(self):
        return "<Article:(id:%s,title:%s)>" % (self.id,self.title)
