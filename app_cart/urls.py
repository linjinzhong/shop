from django.urls import path, include
from . import views

# 应用名，模版中防止不同应用相同路由
app_name = "cart"

urlpatterns = [
    path("add/", views.CartAddView.as_view(), name="add"),  # 购物车记录添加
    path("delete/", views.CartDeleteView.as_view(), name="delete"),  # 购物车记录删除
    path("update/", views.CartUpdateView.as_view(), name="update"),  # 购物车记录更新
    path("", views.CartInfoView.as_view(), name="show"),  # 购物车页面显示
]
