# Generated by Django 4.2 on 2023-07-15 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_goods', '0004_alter_goodsimage_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodsimage',
            name='image',
            field=models.ImageField(upload_to='goods/<property object at 0x7f59ee4fa680>/<property object at 0x7f59ee4fa6d0>', verbose_name='图片路径'),
        ),
    ]
