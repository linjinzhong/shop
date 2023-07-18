from collections import OrderedDict
from django.utils.text import capfirst
from django.contrib import admin
from django.core.cache import cache
from app_user.models import (
    User,
    Address,
)

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    """用户模型类"""

    # 展示字段
    list_display = [
        "id",
        "username",
        "email",
        "is_active",
        "is_superuser",
        "last_login",
        "date_joined",
        "is_delete",
        "create_time",
        "update_time",
    ]

    # 排序字段
    ordering = ("id",)

    # 可编辑字段
    list_editable = ["is_active"]

    # 可展示链接
    list_display_links = ["id", "username"]

    # 过滤
    list_filter = ["is_delete", "is_active"]

    # 分页每页数量
    list_per_page = 20

    # 动作选项位置
    actions_on_top = True
    actions_on_bottom = True

    # 搜索字段
    search_fields = ["username", "email"]


class AddressAdmin(admin.ModelAdmin):
    """地址模型类"""

    # 展示字段
    list_display = [
        "id",
        "user",
        "receiver",
        "addr",
        "zip_code",
        "phone",
        "is_default",
        "is_delete",
        "create_time",
        "update_time",
    ]

    # 排序字段
    ordering = ("id",)

    # 可编辑字段
    list_editable = ["is_default"]

    # 可展示链接
    list_display_links = ["id", "user"]

    # 过滤
    list_filter = ["is_delete", "is_default"]

    # 分页每页数量
    list_per_page = 20

    # 动作选项位置
    actions_on_top = True
    actions_on_bottom = True

    # 搜索字段
    search_fields = ["user", "receiver", "phone"]


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


admin.site.register(User, UserAdmin)  # 用户模型类
admin.site.register(Address, AddressAdmin)  # 地址模型类
