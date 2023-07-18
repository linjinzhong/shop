from collections import OrderedDict
from django.utils.text import capfirst
from django.contrib import admin
from django.core.cache import cache
from app_goods.models import (
    GoodsType,
    GoodsSPU,
    GoodsSKU,
    GoodsImage,
    IndexPromotionBanner,
    IndexGoodsBanner,
    IndexTypeGoodsBanner,
)

# Register your models here.


# 基类 注重对象的重写 多态 父类拥有 让子类继承，那样就不用每个子类进行重写
# 传承：一对多的情况
# 继承：认爸爸的过程
class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """新增或更新表中的数据时调用 方法重写多态"""
        super().save_model(request, obj, form, change)

        # 发出任务, 让celery worker重新生成首页静态页
        from celery_tasks.tasks import generate_static_index_html

        # generate_static_index_html.delay()

        # 清除首页的缓存数据
        cache.delete("index_page_data")

    def delete_model(self, request, obj):
        """删除表中的数据时调用"""
        super().delete_model(request, obj)
        from celery_tasks.tasks import generate_static_index_html

        # generate_static_index_html.delay()

        # 清除首页的缓存数据
        cache.delete("index_page_data")


class IndexGoodsBannerAdmin(BaseModelAdmin):
    """首页轮播商品展示模型类"""

    # 展示字段
    list_display = [
        "id",
        "sku",
        "image",
        "index",
        "is_delete",
        "create_time",
        "update_time",
    ]

    # 排序字段
    ordering = ("id",)

    # 可编辑字段
    list_editable = ["index"]

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
    search_fields = ["sku"]


class IndexPromotionBannerAdmin(BaseModelAdmin):
    """首页促销活动模型类"""

    # 展示字段
    list_display = [
        "id",
        "name",
        "url",
        "image",
        "index",
        "is_delete",
        "create_time",
        "update_time",
    ]

    # 排序字段
    ordering = ("id",)

    # 可编辑字段
    list_editable = ["index"]

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
    search_fields = ["name"]


class IndexTypeGoodsBannerAdmini(BaseModelAdmin):
    """首页分类商品展示模型类"""

    # 展示字段
    list_display = [
        "id",
        "type",
        "sku",
        "display_type",
        "index",
        "is_delete",
        "create_time",
        "update_time",
    ]

    # 排序字段
    ordering = ("id",)

    # 可编辑字段
    list_editable = ["index"]

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
    search_fields = [""]


class GoodsTypeAdmin(BaseModelAdmin):
    """商品种类"""

    # 展示字段
    list_display = [
        "id",
        "name",
        "logo",
        "image",
        "is_delete",
        "create_time",
        "update_time",
    ]

    # 排序字段
    ordering = ("id",)

    # 可编辑字段
    list_editable = ["name"]

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
    search_fields = ["id", "name", "logo"]


class GoodsSPUAdmin(BaseModelAdmin):
    """商品种类"""

    # 展示字段
    list_display = [
        "id",
        "name",
        "detail",
        "is_delete",
        "create_time",
        "update_time",
    ]

    # 排序字段
    ordering = ("id",)

    # 可编辑字段
    list_editable = [
        "name",
    ]

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
    search_fields = ["id", "name"]


class GoodsSKUAdmin(BaseModelAdmin):
    """商品种类"""

    # 展示字段
    list_display = [
        "id",
        "type",
        "goods_spu",
        "name",
        "desc",
        "price",
        "unite",
        "stock",
        "image",
        "sales",
        "status",
        "is_delete",
        "create_time",
        "update_time",
    ]

    # 排序字段
    ordering = ("id",)

    # 可编辑字段
    list_editable = [
        "name",
        "status",
    ]

    # 可展示链接
    list_display_links = ["id"]

    # 过滤
    list_filter = ["type", "goods_spu", "status", "is_delete"]

    # 分页每页数量
    list_per_page = 20

    # 动作选项位置
    actions_on_top = True
    actions_on_bottom = True

    # 搜索字段
    search_fields = ["id", "name"]


class GoodsImageAdmin(BaseModelAdmin):
    """商品种类"""

    # 展示字段
    list_display = [
        "id",
        "sku",
        "image",
        "is_delete",
        "create_time",
        "update_time",
    ]

    # 排序字段
    ordering = ("id",)

    # 可编辑字段
    list_editable = ["sku"]

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
    search_fields = ["id", "sku"]


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


admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)  # 首页轮播商品展示模型类
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)  # 首页促销活动模型类
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmini)  # 首页分类商品展示模型类
admin.site.register(GoodsType, GoodsTypeAdmin)  # 商品种类
admin.site.register(GoodsSPU, GoodsSPUAdmin)  # 商品SPU
admin.site.register(GoodsSKU, GoodsSKUAdmin)  # 商品SKU
admin.site.register(GoodsImage, GoodsImageAdmin)  # 商品图片
