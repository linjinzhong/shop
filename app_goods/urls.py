from django.urls import path
from . import views

# 应用名，模版中防止不同应用相同路由
app_name = "goods"

urlpatterns = [
    path("", views.index, name="index"),  # 首页
]
