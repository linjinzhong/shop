# Generated by Django 4.2 on 2023-07-15 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_goods', '0002_alter_goodsspu_detail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodsimage',
            name='image',
            field=models.ImageField(upload_to='goods/<property object at 0x7fe5c43e0680>/<property object at 0x7fe5c43e06d0>', verbose_name='图片路径'),
        ),
    ]
