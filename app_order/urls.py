from django.urls import path, include
from . import views

# 应用名，模版中防止不同应用相同路由
app_name = "order"

urlpatterns = [
    path("place/", views.OrderPlaceView.as_view(), name="place"),  # 提交订单页面显示
    path("commit/", views.OrderCommitView.as_view(), name="commit"),  # 提交创建订单
    path("pay/", views.OrderPayView.as_view(), name="pay"),  # 订单支付
    path("check/", views.CheckPayView.as_view(), name="check"),  # 查询支付订单结果
    path("confirm/", views.OrderConfirmView.as_view(), name="confirm"),  # 确认收货
    path(
        "comment/<int:order_id>/", views.CommentView.as_view(), name="comment"
    ),  # 订单评论
]
