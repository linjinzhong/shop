from django.db import models
from django.contrib.auth.models import AbstractUser
from common.base_model import BaseModel
# Create your models here.


class User(AbstractUser, BaseModel):
    """用户模型类"""

    class Meta:
        db_table = "tb_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name


class AddressManager(models.Manager):
    """地址模型管理器类"""
    
    def get_default_address(self, user):
        """获取用户默认的收货地址"""
        try:
            address = self.model.objects.get(user=user, is_default=True)
        except self.model.DoesNotExist:
            address = None
        return address


class Address(BaseModel):
    """地址模型类"""
    user = models.ForeignKey("User", verbose_name="所属用户")
    receiver = models.CharField(verbose_name="收件人", max_length=32)
    addr = models.CharField(verbose_name="收件地址", max_length=256)
    zip_code = models.CharField(verbose_name="邮政编码", max_length=6, blank=True)
    phone = models.CharField(verbose_name="联系电话", max_length=11)
    is_default = models.BooleanField(verbose_name="是否默认", default=False)

    objects = AddressManager()

    class Meta:
        db_table = "tb_address"
        verbose_name = "地址"
        verbose_name_plural = verbose_name

    def __str__(self):
        """用户名-收件人-电话"""
        return "%s-%s-%s" % (self.user.username, self.receiver, self.phone)
