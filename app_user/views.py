from django.shortcuts import render, redirect
from django.views.generic import View
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.conf import settings
from django_redis import get_redis_connection
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import SignatureExpired
from celery_tasks.tasks import send_register_active_email
from app_user.models import User, Address
from app_goods.models import GoodsSKU
from app_order.models import OrderInfo, OrderGoods
from utils.mixin import LoginRequiredMixin

import re
import logging

# Create your views here.


LOGGER = logging.getLogger(__name__)


# /user/register
class RegisterView(View):
    """用户注册"""

    def get(self, request):
        """显示注册页面"""
        return render(request, "register.html")

    def post(self, request):
        """进行注册"""

        username = request.POST.get("user_name")
        pwd = request.POST.get("pwd")
        cpwd = request.POST.get("cpwd")
        email = request.POST.get("email")
        allow = request.POST.get("allow")

        LOGGER.info("===>>>|用户注册| %s | %s |", username, email)

        # 非空校验
        if not all([username, pwd, email, allow]):
            return render(request, "register.html", {"errmsg": "数据不完整"})

        # 长度校验
        if len(username) < 5 or len(username) > 20:
            return render(request, "register.html", {"errmsg": "用户名长度不规范"})

        if len(pwd) < 8 or len(pwd) > 20:
            return render(request, "register.html", {"errmsg": "密码长度不规范"})

        # 密码一致性校验
        if pwd != cpwd:
            LOGGER.error("===>>>|用户注册| %s | %s |密码不一致|", username, email)
            return render(request, "register.html", {"errmsg": "密码不一致"})

        # 校验邮箱
        if not re.match(r"^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
            LOGGER.error("===>>>|用户注册| %s | %s |邮箱格式不正确|", username, email)
            return render(request, "register.html", {"errmsg": "邮箱格式不正确"})

        # 校验勾选协议
        if allow != "on":
            LOGGER.error("===>>>|用户注册| %s | %s |请同意协议|", username, email)
            return render(request, "register.html", {"errmsg": "请同意协议"})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:  # 用户名已存在
            return render(request, "register.html", {"errmsg": "用户名已存在"})

        # 业务处理
        user = User.objects.create_user(username, email, pwd)
        user.is_active = 0  # 激活字段
        user.save()

        # 发送邮件激活 /user/active/用户id
        # 激活链接中的身份信息要加密
        auth_s = URLSafeTimedSerializer(settings.SECRET_KEY, "itsdangerous_salt")
        info = {"confirm": user.id}
        token = auth_s.dumps(info)

        # 发邮件
        send_register_active_email.delay(email, username, token)

        # 注册成功，返回首页
        return redirect(reverse("goods:index"))


# /user/active
class ActiveView(View):
    """用户激活"""

    def get(self, reququest, token):
        """用户激活"""
        # 解密
        auth_s = URLSafeTimedSerializer(settings.SECRET_KEY, "itsdangerous_salt")
        try:
            data = auth_s.loads(token, max_age=180)  # 超时3分钟

            user_id = data["confirm"]

            # 根据id获取用户的信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转到登录页面
            return redirect(reverse("user:login"))
        except SignatureExpired as err:
            return HttpResponse("激活链接已过期")
        except Exception as err:
            return HttpResponse("激活失败，%s" % err)


# /user/login
class LoginView(View):
    """用户登录"""

    def get(self, request):
        """显示登录页"""
        # 判断是否记住用户名
        if "username" in request.COOKIES:
            username = request.COOKIES.get("username")
            checked = "checked"
        else:
            username = ""
            checked = ""
        return render(request, "login.html", {"username": username, "checked": checked})

    def post(self, request):
        """登录校验"""

        # 接收数据
        username = request.POST.get("username")
        password = request.POST.get("pwd")

        # 校验数据
        if not all([username, password]):
            return render(request, "login.html", {"errmsg": "数据不完整"})

        # 登录校验
        user = authenticate(username=username, password=password)
        if user is not None:  # 用户名和密码正确
            if user.is_active:  # 已激活
                # 记录用户登录状态
                login(request, user)

                # 获取登录后所要跳转到的地址
                # 默认跳转到首页
                # next_url = request.GET.get("next", reverse("goods:index"))
                next_url = request.GET.get("next", reverse("user:user"))

                # 跳转到首页
                response = redirect(next_url)

                # 判断是否需要记录用户名
                remember = request.POST.get("remember")
                if remember == "on":  # 记住用户名
                    response.set_cookie("username", username, max_age=7 * 24 * 3600)
                else:
                    response.delete_cookie("username")
                return response
            else:  # 未激活
                return render(request, "login.html", {"errmsg": "账户未激活"})
        else:  # 用户名或密码错误
            return render(request, "login.html", {"errmsg": "用户名或密码错误"})


# /user/logout
class LogoutView(View):
    """退出登录"""

    def get(self, request):
        """退出登录"""

        # 清除用户的session信息
        logout(request)

        # 跳转到首页
        return redirect(reverse("goods:index"))


# /user
class UserInfoView(LoginRequiredMixin, View):
    """用户中心-信息页"""

    def get(self, request):
        """显示"""

        # page='user'
        # 如果用户未登录->AnonymousUser类的一个实例
        # 如果用户登录->User类的一个实例
        # request.user.is_authenticated
        # 除了你给模板文件传递的模板变量之外，django框架会把request.user也传给模板文件

        # 获取用户的个人信息
        user = request.user
        address = Address.objects.get_default_address(user)

        # 获取用户的历史记录
        conn = get_redis_connection("history")

        history_key = "history_%d" % user.id

        # 获取用户最新浏览的5个商品的id
        sku_ids = conn.lrange(history_key, 0, 4)

        # 从数据库中查询用户浏览的商品的具体信息
        goods_li = GoodsSKU.objects.filter(id__in=sku_ids)

        # 第一种方式
        goods_list = []
        for sku_id in sku_ids:
            for goods in goods_li:
                if int(sku_id) == goods.id:
                    goods_list.append(goods)

        # 组织上下文
        context = {
            # "page": "user",
            "address": address,
            "goods_list": goods_list,
        }

        return render(request, "user_center_info.html", context)


# /user/order
class UserOrderView(LoginRequiredMixin, View):
    """用户中心-订单页"""

    def get(self, request, page):
        """显示"""

        # 获取用户的订单信息
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by("-create_time")

        # 便利获取订单商品的信息
        for order in orders:
            # 根据order_id查询订单商品信息
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)
            # 便利order_skus计算商品的小计
            for order_sku in order_skus:
                # 计算小计
                amount = order_sku.count * order_sku.price
                # 动态给order_sku增加属性amount，保存订单商品的小计
                order_sku.amount = amount
            order.status_name = OrderInfo.ORDER_STATUS[order.status]
            # 动态给order增加属性，保存订单商品的信息
            order.order_skus = order_skus

        # 分页
        paginator = Paginator(orders, 3)

        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        order_page = paginator.page(page)

        # 进行页码的控制，页面上最多显示5个页码
        # 1.总页数小于5页，页面上显示所有页码
        # 2.如果当前页是前3页，显示1-5页
        # 3.如果当前页是后3页，显示后5页
        # 4.其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        # 组织上下文
        context = {
            "page": "order",
            "order_page": order_page,
            "pages": pages,
        }

        return render(request, "user_center_order.html", context)


# /uesr/address
class UserAddressView(LoginRequiredMixin, View):
    """用户中心-地址页"""

    def get(self, request):
        """地址显示"""

        # page='address'
        # 获取登录用户的对应的User对象
        user = request.user

        # 获取用户的默认收货地址
        address_default = Address.objects.get_default_address(user)
        address_other = Address.objects.filter(user=user, is_default=False)

        context = {
            "page": "address",
            "address_default": address_default,
            "address_other": address_other,
        }
        return render(request, "user_center_site.html", context)

    def post(self, request):
        """地址的添加"""

        # 接受数据
        receiver = request.POST.get("receiver")
        addr = request.POST.get("addr")
        zip_code = request.POST.get("zip_code")
        phone = request.POST.get("phone")

        # 校验数据
        if not all([receiver, addr, phone]):
            return render(request, "user_center_site.html", {"errmsg": "数据不完整"})

        # 校验手机号
        if not re.match(r"^1[3|4|5|7|8][0-9]{9}$", phone):
            return render(request, "user_center_site.html", {"errmsg": "手机格式不正确"})

        # 业务处理：地址添加
        # 如果用户已存在默认收获地址，添加的地址不作为默认收货地址，否则作为默认收货地址
        # 获取登录用户的对应的User对象
        user = request.user
        address = Address.objects.get_default_address(user)

        if address:
            is_default = False
        else:
            is_default = True

        # 添加地址
        Address.objects.create(
            user=user,
            receiver=receiver,
            addr=addr,
            phone=phone,
            zip_code=zip_code,
            is_default=is_default,
        )

        # 返回应答,刷新地址页面 get请求
        return redirect(reverse("user:address"))
