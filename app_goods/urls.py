from django.urls import path
from . import views

# 应用名，模版中防止不同应用相同路由
app_name = "goods"

urlpatterns = [
    path("index/", views.IndexView.as_view(), name="index"),  # 首页
    path("detail/<int:goods_id>/", views.DetailView.as_view(), name="detail"),  # 详情页
    path("list/<int:type_id>/<int:page>", views.ListView.as_view(), name="list"),  # 列表页
]
