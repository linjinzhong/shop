"""models"""
from django.db import models
from common.base_model import BaseModel

# Create your models here.


class OrderInfo(BaseModel):
    """订单模型类"""

    PAY_METHODS = {
        "1": "货到付款",
        "2": "微信支付",
        "3": "支付宝",
        "4": "银联支付",
    }

    PAY_METHODS_CHOICES = {
        (1, "货到付款"),
        (2, "微信支付"),
        (3, "支付宝"),
        (4, "银联支付"),
    }

    ORDER_STATUS = {
        1: "待付款",
        2: "待发货",
        3: "待收货",
        4: "待评价",
        5: "已完成",
        6: "已取消",
        7: "已退款",
    }

    ORDER_STATUS_CHOICES = (
        (1, "待付款"),
        (2, "待发货"),
        (3, "待收货"),
        (4, "待评价"),
        (5, "已完成"),
        (6, "已取消"),
        (7, "已退款"),
    )

    order_id = models.CharField(verbose_name="订单id", primary_key=True, max_length=128)
    user = models.ForeignKey(
        "app_user.User", verbose_name="用户", on_delete=models.PROTECT
    )
    addr = models.ForeignKey(
        "app_user.Address", verbose_name="地址", on_delete=models.PROTECT
    )
    pay_method = models.SmallIntegerField(
        verbose_name="支付方式", default=3, choices=PAY_METHODS_CHOICES
    )
    total_count = models.IntegerField(verbose_name="商品数量", default=1)
    total_price = models.DecimalField(
        verbose_name="商品总价", max_digits=10, decimal_places=2
    )
    transit_price = models.DecimalField(
        verbose_name="订单运费", max_digits=10, decimal_places=2
    )
    status = models.SmallIntegerField(
        verbose_name="订单状态", choices=ORDER_STATUS_CHOICES, default=1
    )
    trade_no = models.CharField(verbose_name="支付编号", max_length=128, default="")
    comment = models.CharField(
        verbose_name="订单备注", max_length=128, default="", blank=True
    )

    class Meta:  # pylint: disable=C0115
        db_table = "tb_order_info"
        verbose_name = "订单信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        """订单id-订单状态"""
        return "%s-%s" % (self.order_id, self.get_status_display())


class OrderGoods(BaseModel):
    """订单商品模型类"""

    order = models.ForeignKey("OrderInfo", verbose_name="订单", on_delete=models.CASCADE)
    sku = models.ForeignKey(
        "app_goods.GoodsSKU", verbose_name="商品SKU", on_delete=models.PROTECT
    )
    count = models.IntegerField(verbose_name="商品数目", default=1)
    price = models.DecimalField(verbose_name="商品价格", max_digits=10, decimal_places=2)
    comment = models.CharField(
        verbose_name="商品评论", max_length=256, default="", blank=True
    )

    class Meta:  # pylint: disable=C0115
        db_table = "tb_order_goods"
        verbose_name = "订单商品"
        verbose_name_plural = verbose_name

    def __str__(self):
        """订单id-商品id(商品名)"""
        return "%s-%s(%s)" % (
            self.order.order_id,
            self.sku.id,
            self.sku.name,
        )
