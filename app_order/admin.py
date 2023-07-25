from collections import OrderedDict
from django.utils.text import capfirst
from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.cache import cache
from app_order.models import (
    OrderGoods,
    OrderInfo,
)
from common.pay_class import AliPayClass


# Register your models here.


class InlineOrderGoods(admin.StackedInline):
    # class InlineOrderGoods(admin.TabularInline):

    """内敛订单下所有商品"""

    model = OrderGoods
    extra = 0


class OrderInfoAdmin(admin.ModelAdmin):
    """订单模型类"""

    # 展示字段
    list_display = [
        "order_id",
        "user",
        "addr",
        "pay_method",
        "total_count",
        "total_price",
        "transit_price",
        "status",
        "is_delete",
        "create_time",
        "update_time",
    ]

    # 排序字段
    ordering = ("create_time",)

    # 可编辑字段
    list_editable = []

    # 可展示链接
    list_display_links = ["order_id"]

    # 过滤
    list_filter = ["is_delete", "status", "pay_method"]

    # 分页每页数量
    list_per_page = 20

    # 动作选项位置
    actions_on_top = True
    actions_on_bottom = True

    # 搜索字段
    search_fields = ["order_id", "user"]

    # 内链该订单下所有商品
    inlines = [
        InlineOrderGoods,
    ]

    def save_model(self, request, obj, form, change):
        """新增或更新表中的数据时调用 方法重写多态"""

        if change and "status" in form.changed_data and obj.status == 7:
            order_id = obj.order_id
            refund_amount = float(obj.total_price + obj.transit_price)

            class_alipay = AliPayClass()
            response = class_alipay.refund(order_id, refund_amount)
            code = response.get("code")
            if code == "10000" and response.get("fund_change") == "Y":
                # 退款成功
                obj.status = 7  # 已退款
            else:  # 退款出错
                messages.set_level(request, messages.ERROR)
                messages.error(request, "订单-%s，退款出错" % order_id)
                return
        super().save_model(request, obj, form, change)


class OrderGoodsAdmin(admin.ModelAdmin):
    """订单商品模型类"""

    # 展示字段
    list_display = [
        "id",
        "order",
        "sku",
        "count",
        "price",
        "comment",
        "is_delete",
        "create_time",
        "update_time",
    ]

    # 排序字段
    ordering = ("id",)

    # 可编辑字段
    list_editable = []

    # 可展示链接
    list_display_links = ["id"]

    # 过滤
    list_filter = ["is_delete"]

    # 分页每页数量
    list_per_page = 20

    # 动作选项位置
    actions_on_top = True
    actions_on_bottom = True

    # 搜索字段
    search_fields = ["order", "sku"]


def _find_model_index(name):
    """定位model注册顺序"""
    count = 0
    for model, _ in admin.site._registry.items():
        if capfirst(model._meta.verbose_name_plural) == name:
            return count
        count += 1
    return count


def _index_decorator(func):
    """model index装饰器"""

    def inner(*args, **kwargs):
        templateresponse = func(*args, **kwargs)
        for app in templateresponse.context_data["app_list"]:
            app["models"].sort(key=lambda x: _find_model_index(x["name"]))
        return templateresponse

    return inner


# admin 设置按注册顺序展示
registry = OrderedDict()
registry.update(admin.site._registry)
admin.site._registry = registry
admin.site.index = _index_decorator(admin.site.index)
admin.site.app_index = _index_decorator(admin.site.app_index)


admin.site.register(OrderInfo, OrderInfoAdmin)  # 订单模型类
admin.site.register(OrderGoods, OrderGoodsAdmin)  # 订单商品模型类
