# Generated by Django 4.2 on 2023-07-15 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_goods', '0003_alter_goodsimage_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodsimage',
            name='image',
            field=models.ImageField(upload_to='goods/<property object at 0x7f11d9faa6d0>/<property object at 0x7f11d9faa720>', verbose_name='图片路径'),
        ),
    ]
