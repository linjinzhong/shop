# Generated by Django 4.2 on 2023-07-15 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_goods', '0005_alter_goodsimage_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodsimage',
            name='image',
            field=models.ImageField(upload_to='goods/<property object at 0x7f032eebe680>/<property object at 0x7f032eebe6d0>', verbose_name='图片路径'),
        ),
    ]
