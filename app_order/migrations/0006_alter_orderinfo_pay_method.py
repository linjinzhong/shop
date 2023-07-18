# Generated by Django 4.2 on 2023-07-15 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_order', '0005_alter_orderinfo_pay_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='pay_method',
            field=models.SmallIntegerField(choices=[(1, '货到付款'), (3, '支付宝'), (2, '微信支付'), (4, '银联支付')], default=3, verbose_name='支付方式'),
        ),
    ]
