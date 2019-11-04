from .models import *
from django.db import models

class hot_Info_View(models.Model):
    time = models.DateTimeField()
    article_id = models.IntegerField()
    user_id = models.IntegerField()
    type = models.IntegerField()

    class Meta:
        db_table = 'hot_view'
        unique_together=("article_id","type")