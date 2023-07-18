#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import traceback
from django.conf import settings
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.FileItem import FileItem
from alipay.aop.api.domain.AlipayTradeAppPayModel import AlipayTradeAppPayModel
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
from alipay.aop.api.domain.AlipayTradePayModel import AlipayTradePayModel
from alipay.aop.api.domain.GoodsDetail import GoodsDetail
from alipay.aop.api.domain.SettleDetailInfo import SettleDetailInfo
from alipay.aop.api.domain.SettleInfo import SettleInfo
from alipay.aop.api.domain.SubMerchant import SubMerchant
from alipay.aop.api.request.AlipayOfflineMaterialImageUploadRequest import (
    AlipayOfflineMaterialImageUploadRequest,
)
from alipay.aop.api.request.AlipayTradeAppPayRequest import AlipayTradeAppPayRequest
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
from alipay.aop.api.request.AlipayTradePayRequest import AlipayTradePayRequest
from alipay.aop.api.response.AlipayOfflineMaterialImageUploadResponse import (
    AlipayOfflineMaterialImageUploadResponse,
)
from alipay.aop.api.response.AlipayTradePayResponse import AlipayTradePayResponse

LOGGER = logging.getLogger("pay")


class AliPayClass(object):
    """支付宝支付类"""

    def __init__(self) -> None:
        """
        设置配置，包括支付宝网关地址、app_id、应用私钥、支付宝公钥等，其他配置值可以查看AlipayClientConfig的定义。
        """
        self.conf_alipay = settings.PAY_ALIPAY_TEST
        self.alipay_client_config = AlipayClientConfig()
        self.alipay_client_config.server_url = self.conf_alipay["gateway"]
        self.alipay_client_config.app_id = self.conf_alipay["appid"]
        self.alipay_client_config.app_private_key = self.conf_alipay["app_private_key"]
        self.alipay_client_config.alipay_public_key = self.conf_alipay[
            "alipay_public_key"
        ]
        """
        得到客户端对象。
        注意，一个alipay_client_config对象对应一个DefaultAlipayClient，定义DefaultAlipayClient对象后，alipay_client_config不得修改，如果想使用不同的配置，请定义不同的DefaultAlipayClient。
        logger参数用于打印日志，不传则不打印，建议传递。
        """
        self.client = DefaultAlipayClient(
            alipay_client_config=self.alipay_client_config, logger=LOGGER
        )

    def pay(self, order_id, total_amount, subject):
        """
        页面接口示例：alipay.trade.page.pay(统一收单下单并支付页面接口)
        sdk的demo有问题，需要根据官网填必填参数即可
        https://opendocs.alipay.com/open/59da99d0_alipay.trade.page.pay?pathHash=8e24911d&ref=api
        """
        # 对照接口文档，构造请求对象
        model = AlipayTradePagePayModel()
        model.out_trade_no = order_id
        model.total_amount = total_amount
        model.subject = subject
        # model.body = "jesonlin测试"
        model.product_code = "FAST_INSTANT_TRADE_PAY"
        # settle_detail_info = SettleDetailInfo()
        # settle_detail_info.amount = total_amount
        # settle_detail_info.trans_in_type = "userId"
        # settle_detail_info.trans_in = self.conf_alipay["userid"]
        # settle_detail_infos = list()
        # settle_detail_infos.append(settle_detail_info)
        # settle_info = SettleInfo()
        # settle_info.settle_detail_infos = settle_detail_infos
        # model.settle_info = settle_info
        # sub_merchant = SubMerchant()
        # sub_merchant.merchant_id = self.conf_alipay["pid"]
        # model.sub_merchant = sub_merchant
        request = AlipayTradePagePayRequest(biz_model=model)

        # 得到构造的请求，如果http_method是GET，则是一个带完成请求参数的url，如果http_method是POST，则是一段HTML表单片段
        response = self.client.page_execute(request, http_method="GET")  # 返回支付链接
        LOGGER.info(
            "======|alipay.trade.page.pay response:%s|order_id:%s|", response, order_id
        )
        return response

    def check(self, order_id):
        """
        页面接口示例：alipay.trade.query(统一收单交易查询)
        sdk的demo有问题，需要根据官网填必填参数即可
        https://opendocs.alipay.com/open/bff76748_alipay.trade.query?pathHash=e3ddce1d&ref=api&scene=23
        """
        # 对照接口文档，构造请求对象
        model = AlipayTradeQueryModel()
        model.out_trade_no = order_id
        model.query_options = ["trade_settle_info"]
        request = AlipayTradeQueryRequest(biz_model=model)

        # 得到构造的请求，如果http_method是GET，则是一个带完成请求参数的url，如果http_method是POST，则是一段HTML表单片段
        response = self.client.execute(request)
        response = json.loads(response)
        LOGGER.info(
            "======|alipay.trade.query response:%s|order_id:%s|", response, order_id
        )
        return response
