from django.urls import path, include
from . import views

# 应用名，模版中防止不同应用相同路由
app_name = "user"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),  # 注册
    path("active/<str:token>", views.ActiveView.as_view(), name="active"),  # 激活
    path("login/", views.LoginView.as_view(), name="login"),  # 登录
    path("logout/", views.LogoutView.as_view(), name="logout"),  # 登出

    path("", views.UserInfoView.as_view(), name="user"), # 用户中心-信息页
    path("order/<int:page>", views.UserOrderView.as_view(), name="order"), # 用户中心-订单页
    path("address/", views.UserAddressView.as_view(), name="address"), # 用户中心-地址页
]
