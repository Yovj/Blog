from django.urls import path
from . import views

app_name = 'article'


urlpatterns = [
    path("modify/",views.publish_Blog),
    path("del/",views.delete_Blog),
    path('detail/',views.get_blogDetail)
]