from django.urls import path, include
from . import views

# 应用名，模版中防止不同应用相同路由
app_name = "order"

urlpatterns = [
    path("index/", views.index, name="index"),  # 注册
]
