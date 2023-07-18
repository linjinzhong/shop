"""models"""
import os
from django.db import models
from common.base_model import BaseModel

# from tinymce.models import HTMLField
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.


class GoodsType(BaseModel):
    """商品类型模型类"""

    name = models.CharField(verbose_name="种类名称", max_length=32)
    logo = models.CharField(verbose_name="种类标识", max_length=32)
    image = models.ImageField(verbose_name="种类图片", upload_to="type")

    class Meta:
        db_table = "tb_goods_type"
        verbose_name = "商品种类"
        verbose_name_plural = verbose_name

    def __str__(self):
        """商品种类名"""
        return "%s" % self.name


class GoodsSPU(BaseModel):
    """商品SPU模型类，Standard Product Unit（标准产品单位），SPU是商品信息聚合的最小单位
    比如：iphone14
    """

    name = models.CharField(verbose_name="商品SPU名称", max_length=32)
    # detail = HTMLField(verbose_name="商品详情", blank=True)  # 富文本详情
    detail = RichTextUploadingField(verbose_name="商品详情", blank=True)  # 富文本详情

    class Meta:
        db_table = "tb_goods_spu"
        verbose_name = "商品SPU"
        verbose_name_plural = verbose_name

    def __str__(self):
        """商品SPU名"""
        return "%s" % self.name


class GoodsSKU(BaseModel):
    """商品SKU模型类, Stock Keeping Unit（库存单位），SKU即库存进出计量的单位
    比如：iphone14 + promax + 256 + 黑色
    """

    STATUS_CHOICES = (
        (0, "下架"),
        (1, "上架"),
    )

    def image_dir(self, filename):
        return "goods/{typeid}/{spuid}/{filename}".format(
            typeid=str(self.type.id), spuid=str(self.goods_spu.id), filename=filename
        )

    type = models.ForeignKey("GoodsType", verbose_name="商品种类", on_delete=models.PROTECT)
    goods_spu = models.ForeignKey(
        "GoodsSPU", verbose_name="商品SPU", on_delete=models.CASCADE
    )
    name = models.CharField(verbose_name="商品名称", max_length=32)
    desc = models.CharField(verbose_name="商品简介", max_length=256)
    price = models.DecimalField(verbose_name="商品价格", max_digits=10, decimal_places=2)
    unite = models.CharField(verbose_name="商品单位", max_length=32)
    image = models.ImageField(verbose_name="商品图片", upload_to=image_dir)
    stock = models.IntegerField(verbose_name="商品库存", default=1)
    sales = models.IntegerField(verbose_name="商品销量", default=0)
    status = models.SmallIntegerField(
        verbose_name="商品状态", default=1, choices=STATUS_CHOICES
    )

    class Meta:
        db_table = "tb_goods_sku"
        verbose_name = "商品SKU"
        verbose_name_plural = verbose_name

    def __str__(self):
        """商品种类名-商品SPU名-商品SKUid(商品名)"""
        return "%s-%s-%s(%s)" % (
            self.type.name,
            self.goods_spu.name,
            self.id,
            self.name,
        )

    @property
    def typeid(self):
        return self.id

    @property
    def spuid(self):
        return self.goods_spu.id


class GoodsImage(BaseModel):
    """商品图片模型"""

    @property
    def typeid(self):
        return self.sku.id

    @property
    def spuid(self):
        return self.sku.goods_spu.id

    def image_dir(self, filename):
        return "goods/{typeid}/{spuid}/{filename}".format(
            typeid=str(self.sku.type.id),
            spuid=str(self.sku.goods_spu.id),
            filename=filename,
        )

    sku = models.ForeignKey("GoodsSKU", verbose_name="商品SKU", on_delete=models.CASCADE)
    image = models.ImageField(verbose_name="图片路径", upload_to=image_dir)

    class Meta:
        db_table = "tb_goods_image"
        verbose_name = "商品图片"
        verbose_name_plural = verbose_name

    def __str__(self):
        """商品id(商品名)"""
        return "%s(%s)" % (self.sku.id, self.sku.name)


class IndexGoodsBanner(BaseModel):
    """首页轮播商品展示模型类"""

    sku = models.ForeignKey("GoodsSKU", verbose_name="商品SKU", on_delete=models.CASCADE)
    image = models.ImageField(verbose_name="图片", upload_to="banner")
    index = models.SmallIntegerField(verbose_name="展示顺序", default=0)

    class Meta:
        db_table = "tb_index_banner"
        verbose_name = "主页轮播商品"
        verbose_name_plural = verbose_name

    def __str__(self):
        """轮播商品名id(商品名)-顺序"""
        return "%s(%s)-%s" % (self.sku.id, self.sku.name, self.index)


class IndexPromotionBanner(BaseModel):
    """首页促销活动模型类"""

    name = models.CharField(verbose_name="活动名称", max_length=20)
    url = models.URLField(verbose_name="活动链接")
    image = models.ImageField(verbose_name="活动图片", upload_to="banner")
    index = models.SmallIntegerField(verbose_name="展示顺序", default=0)

    class Meta:
        db_table = "tb_index_promotion"
        verbose_name = "主页促销活动"
        verbose_name_plural = verbose_name

    def __str__(self):
        """促销活动名-顺序"""
        return "%s-%s" % (self.name, self.index)


class IndexTypeGoodsBanner(BaseModel):
    """首页分类商品展示模型类"""

    DISPLAY_TYPE_CHOICES = ((0, "标题"), (1, "图片"))

    type = models.ForeignKey("GoodsType", verbose_name="商品种类", on_delete=models.CASCADE)
    sku = models.ForeignKey("GoodsSKU", verbose_name="商品SKU", on_delete=models.CASCADE)
    display_type = models.SmallIntegerField(
        verbose_name="展示类型", default=1, choices=DISPLAY_TYPE_CHOICES
    )
    index = models.SmallIntegerField(verbose_name="展示顺序", default=0)

    class Meta:
        db_table = "tb_index_type_goods"
        verbose_name = "主页分类展示商品"
        verbose_name_plural = verbose_name

    def __str__(self):
        """分类展示商品id(商品名)-展示类型-顺序"""
        return "%s(%s)-%s-%s" % (
            self.sku.id,
            self.sku.name,
            self.get_display_type_display(),
            self.index,
        )
