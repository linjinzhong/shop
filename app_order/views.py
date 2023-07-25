from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.views.generic import View
from django.urls import reverse
from django.db import transaction
from django.conf import settings
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
from app_user.models import Address
from app_goods.models import GoodsSKU
from app_order.models import OrderInfo, OrderGoods
from datetime import datetime
import time
import logging

from common.pay_class import AliPayClass


LOGGER = logging.getLogger("order")


# Create your views here.


def generate_order_uuid(userid):
    """生成订单编号"""
    order_id = str(datetime.fromtimestamp(int(time.time()))).replace("-", "").replace(
        " ", ""
    ).replace(":", "").replace(".", "") + str(userid).zfill(9)
    return order_id


# /order/place/
class OrderPlaceView(LoginRequiredMixin, View):
    """提交订单页面显示-从购物车提交"""

    def _prepare(self, request, sku_ids):
        LOGGER.info("=============sku_ids=%s|", sku_ids)
        # 获取我们的登录用户
        user = request.user

        # 校验参数
        if not sku_ids:
            return redirect(reverse("cart:show"))

        conn = get_redis_connection("cart")
        cart_key = "cart_%d" % user.id

        skus = []
        # 保存商品的总家属和总价
        total_count = 0
        total_price = 0
        # 便利sku_ids获取用户要购买的商品的信息
        for sku_id in sku_ids:
            # 根据商品的id获取商品的信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 获取用户要购买的商品的数量
            count = conn.hget(cart_key, sku_id)
            # 计算商品的小计
            amount = sku.price * int(count)
            # 动态给sku增加属性count,保存购买商品的数量
            sku.count = int(count)
            # 动态给sku添加属性amount,保存购买商品的小计
            sku.amount = amount
            # 追加
            skus.append(sku)
            # 累加计算商品的总价和总剑术
            total_count += int(count)
            total_price += amount

        # 运费： 实际开发的时候，属于一个子系统
        transit_price = 10  # 写死

        # 是付款
        total_pay = total_price + transit_price

        # 获取用户的首见地址
        addrs = Address.objects.filter(user=user)

        # 组织上下文
        sku_ids = ",".join(sku_ids)  # [1, 25]->1, 25
        context = {
            "skus": skus,
            "total_count": total_count,
            "total_price": total_price,
            "transit_price": transit_price,
            "total_pay": total_pay,
            "addrs": addrs,
            "sku_ids": sku_ids,
        }
        return context

    def get(self, request):
        """立即购买-跳转过来"""

        context = self._prepare(request, [request.GET.get("sku_id")])
        LOGGER.info("======|立即购买|context=%s|", context)

        # 使用模板
        return render(request, "place_order.html", context)

    def post(self, request):
        """提交订单-跳转过来"""

        context = self._prepare(request, request.POST.getlist("sku_ids"))
        LOGGER.info("======|提交订单|context=%s|", context)

        # 使用模板
        return render(request, "place_order.html", context)


# 前端传递的参数: 地址的id 支付方法(pay_method), 用户要购买的商品id
# 悲观锁：执行的时候加琐 用户抢锁
class OrderCommitView(View):
    """订单创建"""

    # 事务装饰器
    @transaction.atomic
    def post(self, request):
        """订单创建"""

        # 判断用户是否登录,非后台无法使用LoginRequiredMixin验证
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"res": 1, "errmsg": "用户未登录"})

        # 接受参数
        addr_id = request.POST.get("addr_id")
        pay_method = request.POST.get("pay_method")
        sku_ids = request.POST.get("sku_ids")

        # 校验参数
        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({"res": 2, "errmsg": "参数不完整"})

        # 校验支付方式
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({"res": 3, "errmsg": "非法的支付方式"})

        # 校验地址
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:  # 地址不存在
            return JsonResponse({"res": 4, "errmsg": "地址不存在"})

        # todo: 创建订单核心业务

        # 组织参数
        # 订单id： 年月日时间+用户id
        # order_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(user.id)
        order_id = generate_order_uuid(user.id)

        # 运费先写死
        transit_price = 10

        # 总数量和总金额
        total_count = 0
        total_price = 0

        # 设置事务保存点
        save_id = transaction.savepoint()
        try:
            # 向df_order_info表中添加一条记录
            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                addr=addr,
                pay_method=pay_method,
                total_count=total_count,
                total_price=total_price,
                transit_price=transit_price,
            )

            # 用户的订单中有几个商品，需要向df_order_goods表中加入几条记录
            conn = get_redis_connection("cart")
            cart_key = "cart_%d" % user.id

            sku_ids = sku_ids.split(",")
            for sku_id in sku_ids:
                # 获取商品的信息
                try:
                    # 悲观锁：select * from df_goods_sku where id=sku_id for update; for update 为加琐操作
                    sku = GoodsSKU.objects.select_for_update().get(id=sku_id)
                except:  # 商品不存在
                    transaction.savepoint_rollback(save_id)
                    return JsonResponse({"res": 5, "errmsg": "商品不存在"})

                # 从redis中获取用户所要购买的商品的数量
                count = conn.hget(cart_key, sku_id)

                # 判断商品的库存
                if int(count) > sku.stock:
                    transaction.savepoint_rollback(save_id)
                    return JsonResponse({"res": 6, "errmsg": " 商品库存不足"})

                # 向df_order_goods表中添加一条记录
                OrderGoods.objects.create(
                    order=order, sku=sku, count=count, price=sku.price
                )

                # 更新商品的库存和销量
                sku.stock -= int(count)
                sku.sales += int(count)
                sku.save()

                # 加计算订单商品的总数量和总价格
                amount = sku.price * int(count)
                total_count += int(count)
                total_price += amount

            # 更新订单信息表中的商品的总数量和总价格
            order.total_count = total_count
            order.total_price = total_price
            order.save()
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            return JsonResponse({"res": 7, "errmsg": "下单失败"})

        # 提交事务
        transaction.savepoint_commit(save_id)

        # 清楚用户购物车中对应的记录 [1, 3]
        conn.hdel(cart_key, *sku_ids)  # 拆包

        # 返回应答
        return JsonResponse({"res": 0, "message": "创建成功"})


# ajax　post
# 前端传递的参数： 订单id(order_id)
# /order/pay/
class OrderPayView(View):
    """订单支付"""

    def post(self, request):
        """订单支付"""

        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"res": 1, "errmsg": "用户未登录"})

        # 接收参数
        order_id = request.POST.get("order_id")

        # 校验参数
        if not order_id:
            return JsonResponse({"res": 2, "errmsg": "无效的订单id"})

        # 校验订单
        try:
            order = OrderInfo.objects.get(
                order_id=order_id, user=user, pay_method=3, status=1
            )
        except OrderInfo.DoesNotExist:
            return JsonResponse({"res": 3, "errmsg": "订单不存在"})

        total_amount = float(order.total_price + order.transit_price)
        subject = "卓谨商城-%s" % order_id

        LOGGER.info("======准备支付|order_id=%s|total_amount=%s|", order_id, total_amount)
        class_alipay = AliPayClass()
        ret = class_alipay.pay(order_id, total_amount, subject)

        return JsonResponse({"res": 0, "pay_url": ret})


# ajax post
# 前端传递参数 order_id
# /order/check/
class CheckPayView(View):
    """查询订单支付结果"""

    def post(self, request):
        """查询支付结果"""

        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"res": 1, "errmsg": "用户未登录"})

        # 接收参数
        order_id = request.POST.get("order_id")

        # 校验参数
        if not order_id:
            return JsonResponse({"res": 2, "errmsg": "无效的订单id"})

        try:
            order = OrderInfo.objects.get(
                order_id=order_id, user=user, pay_method=3, status=1
            )
        except OrderInfo.DoesNotExist:
            return JsonResponse({"res": 3, "errmsg": "订单不存在"})

        # 调用支付宝交易查询接口
        while True:
            """
            相应参数
            {
                "code": "10000",
                "msg": "Success",
                "buyer_logon_id": "sfb***@sandbox.com",
                "buyer_pay_amount": "0.00",
                "buyer_user_id": "2088722004609439",
                "buyer_user_type": "PRIVATE",
                "invoice_amount": "0.00",
                "out_trade_no": "20230713203734000000001",
                "point_amount": "0.00",
                "receipt_amount": "0.00",
                "send_pay_date": "2023-07-14 18:27:55",
                "total_amount": "1207.00",
                "trade_no": "2023071422001409430500319605",
                "trade_status": "TRADE_SUCCESS"
            }
            {
                "msg": "Business Failed",
                "code": "40004",
                "out_trade_no": "20230713203318000000001",
                "sub_msg": "交易不存在",
                "sub_code": "ACQ.TRADE_NOT_EXIST",
                "receipt_amount": "0.00",
                "point_amount": "0.00",
                "buyer_pay_amount": "0.00",
                "invoice_amount": "0.00"
            }
            """
            class_alipay = AliPayClass()
            response = class_alipay.check(order_id)
            LOGGER.info("======|检查支付|order_id=%s|response=%s|", order_id, response)

            code = response.get("code")

            if code == "10000" and response.get("trade_status") == "TRADE_SUCCESS":
                # 支付成功
                LOGGER.info("======|支付成功|order_id=%s|", order_id)
                trade_no = response.get("trade_no")  # 获取支付宝交易号
                order.trade_no = trade_no  # 更新订单状态
                order.status = 2  # 待发货
                order.save()
                return JsonResponse({"res": 0, "message": "支付成功"})
            elif code == "40004" or (
                code == "10000" and response.get("trade_status") == "WAIT_BUYER_PAY"
            ):
                # 等待卖家付款  # 业务处理失败，可能一会就会成功
                LOGGER.info("======|支付受阻，开始休眠5秒|order_id=%s|", order_id)
                time.sleep(5)
                continue
            else:  # 支付出错
                LOGGER.info("======|支付出错|order_id=%s|", order_id)
                return JsonResponse(
                    {"res": 4, "errmsg": "支付失败:%s" % response.get("sub_msg")}
                )


# ajax　post
# 前端传递的参数： 订单id(order_id)
# /order/refund/
class OrderRefundView(View):
    """退款"""

    def post(self, request):
        """取消订单-退款"""

        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"res": 1, "errmsg": "用户未登录"})

        # 接收参数
        order_id = request.POST.get("order_id")

        # 校验参数
        if not order_id:
            return JsonResponse({"res": 2, "errmsg": "无效的订单id"})

        try:
            order = OrderInfo.objects.get(
                order_id=order_id, user=user, pay_method=3, status=2
            )
        except OrderInfo.DoesNotExist:
            return JsonResponse({"res": 3, "errmsg": "订单不存在"})

        refund_amount = float(order.total_price + order.transit_price)

        # 调用支付宝交易查询接口
        while True:
            """
            {
                "alipay_trade_refund_response": {
                    "code": "10000",
                    "msg": "Success",
                    "trade_no": "支付宝交易号",
                    "out_trade_no": "6823789339978248",
                    "buyer_logon_id": "159****5620",
                    "fund_change": "Y",
                    "refund_fee": 88.88,
                    "refund_detail_item_list": [
                        {
                            "fund_channel": "ALIPAYACCOUNT",
                            "amount": 10,
                            "real_amount": 11.21,
                            "fund_type": "DEBIT_CARD"
                        }
                    ],
                    "store_name": "望湘园联洋店",
                    "buyer_user_id": "2088101117955611",
                    "send_back_fee": "1.8",
                    "refund_hyb_amount": "10.24",
                    "refund_charge_info_list": [
                        {
                            "refund_charge_fee": 0.01,
                            "switch_fee_rate": "0.01",
                            "charge_type": "trade",
                            "refund_sub_fee_detail_list": [
                                {
                                    "refund_charge_fee": 0.1,
                                    "switch_fee_rate": "0.01"
                                }
                            ]
                        }
                    ]
                },
                "sign": "ERITJKEIJKJHKKKKKKKHJEREEEEEEEEEEE"
            }
            """
            class_alipay = AliPayClass()
            response = class_alipay.refund(order_id, refund_amount)
            LOGGER.info(
                "======|退款|order_id=%s|refund_amount=%s|response=%s|",
                order_id,
                refund_amount,
                response,
            )

            code = response.get("code")

            if code == "10000" and response.get("fund_change") == "Y":
                # 退款成功
                LOGGER.info("======|退款成功|order_id=%s|", order_id)
                order.status = 7  # 已退款
                order.save()
                return JsonResponse({"res": 0, "message": "退款成功"})
            elif code == "20000":
                # 服务不可用，稍后重试
                LOGGER.info("======|退款受阻，开始休眠5秒|order_id=%s|", order_id)
                time.sleep(5)
                continue
            else:  # 退款出错
                LOGGER.info("======|退款出错|order_id=%s|", order_id)
                return JsonResponse(
                    {"res": 4, "errmsg": "退款失败:%s" % response.get("sub_msg")}
                )


# ajax　post
# 前端传递的参数： 订单id(order_id)
# /order/confirm/
class OrderConfirmView(View):
    """确认收货"""

    def post(self, request):
        """确认收货"""

        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"res": 1, "errmsg": "用户未登录"})

        # 接收参数
        order_id = request.POST.get("order_id")

        # 校验参数
        if not order_id:
            return JsonResponse({"res": 2, "errmsg": "无效的订单id"})

        # 校验订单
        try:
            order = OrderInfo.objects.get(
                order_id=order_id, user=user, pay_method=3, status=3
            )
            order.status = 4  # 确认收货后变为待评价
            order.save()
        except OrderInfo.DoesNotExist:
            return JsonResponse({"res": 3, "errmsg": "订单不存在"})

        return JsonResponse({"res": 0, "errmsg": "success"})


# /order/comment/
class CommentView(LoginRequiredMixin, View):
    """订单评论"""

    def get(self, request, order_id):
        """提供评论页面"""

        user = request.user

        # 校验数据
        if not order_id:
            return redirect(reverse("user:order"))

        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))

        # 根据订单的状态获取订单的状态标题
        order.status_name = OrderInfo.ORDER_STATUS[order.status]

        # 获取订单商品信息
        order_skus = OrderGoods.objects.filter(order_id=order_id)
        for order_sku in order_skus:
            # 计算商品的小计
            amount = order_sku.count * order_sku.price
            # 动态给order_sku增加属性amount,保存商品小计
            order_sku.amount = amount
        # 动态给order增加属性order_skus, 保存订单商品信息
        order.order_skus = order_skus

        # 使用模板
        return render(request, "order_comment.html", {"order": order})

    def post(self, request, order_id):
        """处理评论内容"""

        user = request.user
        # 校验数据
        if not order_id:
            return redirect(reverse("user:order"))

        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))

        # 获取评论条数
        total_count = request.POST.get("total_count")
        total_count = int(total_count)

        # 循环获取订单中商品的评论内容
        for i in range(1, total_count + 1):
            # 获取评论的商品的id
            sku_id = request.POST.get("sku_%d" % i)  # sku_1 sku_2
            # 获取评论的商品的内容
            content = request.POST.get(
                "content_%d" % i, ""
            )  # cotent_1 content_2 content_3
            try:
                order_goods = OrderGoods.objects.get(order=order, sku_id=sku_id)
            except OrderGoods.DoesNotExist:
                continue

            order_goods.comment = content
            order_goods.save()

        order.status = 5  # 已完成
        order.save()

        return redirect(reverse("user:order", kwargs={"page": 1}))
