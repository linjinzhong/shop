from django.urls import path, include
from . import views

# 应用名，模版中防止不同应用相同路由
app_name = "cart"

urlpatterns = [
    path("", views.CartInfoView.as_view(), name='show'), # 购物车页面显示
]
