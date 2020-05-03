#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Time :    2020/4/29 0:10
@Author:  LQ
@Email: LQ65534@163.com
@File: auto_operate.py
@Software: PyCharm
"""

import time
import os
import sys
import json
import hashlib
import requests
import random
import string
import ccxt
import log

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

CENTER_COUNT = 50
URL_HOME = "http://openapi.aofex.com"
# TOKEN = "cc75fd5ed194ee77379947d7257b95f6"
# SECRET = "613sjppnl6npw8o6uy3w"

TOKEN = "22c6e4a54643a035b4bcaf903fd72c94"
SECRET = "2z5y19bn4q287v71dx1j"

# 交易对列表
market_symbols_url = "/openApi/market/symbols"
# 市场成交价地址
market_trade_url = "/openApi/market/trade"
# 当前委托列表
entrust_current_list_url = "/openApi/entrust/currentList"
# 历史委托列表
entrust_history_list_url = "/openApi/entrust/historyList"
# 我的资产
my_wallet_list_url = "/openApi/wallet/list"
# 查询成交详情
entrust_detail_url = "/openApi/entrust/detail"
# 撮合挂单
entrust_add_url = "/openApi/entrust/add"


class Market_Trade(object):
    def __init__(self,URL_HOME,token,secret_key):
        self.aofex_url = URL_HOME
        self._token_ = token
        self._secret_key_ = secret_key
        self.log = log.logger

    def get_requests(self, args):
        r = ''
        if not 'timeout' in args:
            args['timeout'] = 60

        if not 'method' in args:
            args['method'] = 'GET'
        else:
            args['method'] = args['method'].upper()

        # header设置
        if not 'headers' in args:
            args['headers'] = {}

        if not 'user-agent' in args['headers']:
            args['headers'][
                'user-agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

        # Cookies
        cookies = {}
        if 'cookies' in args:
            cookies = args['cookies']

        if not 'data' in args:
            args['data'] = {}

        header_data, ran_str, time_stamp = self.mkHeader(args['data'])
        args['headers'].update(header_data)
        if args['method'] == 'GET':
            r = requests.get(args['url'], params=args['data'], cookies=cookies, headers=args['headers'],
                             timeout=int(args['timeout']), verify=False)
        elif args['method'] == 'POST':
            print("******   post  ********")
            args['headers'].update({"Content-Type": "application/x-www-form-urlencoded; boundary=----WebKitFormBoundaryuILbHAxyzWMIAXn2"})
            r = requests.post(args['url'], data=args['data'], cookies=cookies, headers=args['headers'],
                              timeout=int(args['timeout']), verify=False)

        result = {}
        result['code'] = r.status_code
        ck = {}
        for cookie in r.cookies:
            ck.update({cookie.name: cookie.value})
        result['cookies'] = ck
        result['headers'] = r.headers
        result['content'] = r.content
        # print(r.text)
        if result['code'] == 200:
            # logger.info("success",json.loads(result['content'].decode('utf-8')))
            return json.loads(result['content'].decode('utf-8'))
        else:
            # logger.error("failed%s"%result)
            return result

    # http 带签名的header生成方法
    def mkHeader(self, data: dict, random_str=None, time_s=None, is_byte=False):
        ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 5)) if random_str == None else random_str
        time_stamp = int(time.time()) if time_s == None else time_s
        Nonce = "%s_%s" % (time_stamp, ran_str)
        header = dict()
        if is_byte:
            header[b'Token'] = bytes(self._token_, encoding='utf8')
            header[b'Nonce'] = bytes(Nonce, encoding='utf8')
            header[b'Signature'] = bytes(self.sign(Nonce, data), encoding='utf8')
        else:
            header['Token'] = self._token_
            header['Nonce'] = Nonce
            header['Signature'] = self.sign(Nonce, data)
        return header, ran_str, time_stamp

    # 签名生成方法
    def sign(self, Nonce, data: dict):
        tmp = list()
        tmp.append(self._token_)
        tmp.append(self._secret_key_)
        tmp.append(Nonce)
        for d, x in data.items():
            tmp.append(str(d) + "=" + str(x))

        return hashlib.sha1(''.join(sorted(tmp)).encode("utf8")).hexdigest()


    # 查询交易对列表 https://aofex.zendesk.com/hc/zh-cn/articles/360035699954-%E4%BA%A4%E6%98%93%E5%AF%B9%E5%88%97%E8%A1%A8
    def get_market_symbols_url(self):
        self.log.info("获取交易对列表")
        url = URL_HOME + market_symbols_url
        data = {}
        args = dict()
        args['url'] = url
        args['method'] = 'GET'
        args['data'] = dict()
        args['data'] = data
        res = self.get_requests(args)
        return res

    # 查询市场成交价 https://aofex.zendesk.com/hc/zh-cn/articles/360035700034-%E6%9F%A5%E8%AF%A2%E5%B8%82%E5%9C%BA%E6%88%90%E4%BA%A4
    def get_market_trade(self,*args,**kwargs):
        self.log.info("查询市场成交价")
        # symbol 交易对名称
        url = URL_HOME + market_trade_url
        data = {
            "symbol": kwargs.get("symbol","BTC-USDT")
        }
        args = dict()
        args['url'] = url
        args['method'] = 'GET'
        args['data'] = dict()
        args['data'] = data
        res = self.get_requests(args)
        """ 返回数据说明
            "data": [
          {
            "id": 成交id,
            "price": 成交价,
            "amount": 成交量,
            "direction": 主动成交方向,
            "ts": 成交时间
          }
        ]
        """
        result = []
        for tmp in res.get("result", {0: 0}).get("data"):
            data_template = {
                "成交 id": tmp.get("id"),
                "成交价 price": tmp.get("price"),
                "成交量 amount": tmp.get("amount"),
                "主动成交方向 direction": tmp.get("direction"),
                "成交时间 ts": tmp.get("ts")
            }
            result.append(data_template)
        return result

    # 查询当前委托列表 https://aofex.zendesk.com/hc/zh-cn/articles/360035736274-%E5%BD%93%E5%89%8D%E5%A7%94%E6%89%98%E5%88%97%E8%A1%A8
    def get_entrust_current_list(self,*args,**kwargs):
        self.log.info("查询当前委托列表")
        """
        symbol: 交易对(当前交易对必传,全部交易对不传)
        from: 查询起始order_sn
        direct: 查询方向(默认 prev)，prev 向前，时间（或 ID）倒序；
                next 向后，时间（或 ID）正序）。（举例一列数：1，2，3，4，5。from=4，
                prev有3，2，1；next只有5）
        limit: 分页返回的结果集数量，默认为20，最大为100(具体参见分页处的描述)
        :return:
        """
        url = URL_HOME + entrust_current_list_url
        data = {
            "symbol":kwargs.get("symbol",""),
            "from":kwargs.get("from",0),
            "direct":kwargs.get("direct",""),
            "limit":kwargs.get("limit",20),
        }
        args = dict()
        args['url'] = url
        args['method'] = 'GET'
        args['data'] = dict()
        args['data'] = data
        res = self.get_requests(args)
        result = []
        for tmp in res.get("result", {0: 0}):
            data_template = {
                "订单id": tmp.get("order_id"),
                "订单编号": tmp.get("order_sn"),
                "交易对": tmp.get("symbol"),
                "委托时间": tmp.get("ctime"),
                "委托类型": tmp.get("type"),
                "委托方向": tmp.get("side"),
                "价格": tmp.get("price"),
                "委托数量": tmp.get("number"),
                "委托总额": tmp.get("total_price"),
                "已成交数量": tmp.get("deal_number"),
                "已成交均价": tmp.get("deal_price"),
                "状态": tmp.get("status"),

            }
            result.append(data_template)
        return result

    # 查询历史委托列表 https://aofex.zendesk.com/hc/zh-cn/articles/360035736674-%E5%8E%86%E5%8F%B2%E5%A7%94%E6%89%98%E5%88%97%E8%A1%A8
    def get_entrust_history_list(self,*args,**kwargs):
        self.log.info("查询委托列表")
        """
        symbol: 交易对(当前交易对必传,全部交易对不传)
        from: 查询起始order_sn
        direct: 查询方向(默认 prev)，prev 向前，时间（或 ID）倒序；
                next 向后，时间（或 ID）正序）。（举例一列数：1，2，3，4，5。from=4，
                prev有3，2，1；next只有5）
        limit: 分页返回的结果集数量，默认为20，最大为100(具体参见分页处的描述)
        :return:
        """
        url = URL_HOME + entrust_history_list_url
        data = {
            "symbol":kwargs.get("symbol",""),
            "from":kwargs.get("from",0),
            "direct":kwargs.get("direct",""),
            "limit":kwargs.get("limit",20),
        }
        args = dict()
        args['url'] = url
        args['method'] = 'GET'
        args['data'] = dict()
        args['data'] = data
        res = self.get_requests(args)
        result = []
        for tmp in res.get("result", {0: 0}):
            data_template = {
                "订单id": tmp.get("order_id"),
                "订单编号": tmp.get("order_sn"),
                "交易对": tmp.get("symbol"),
                "委托时间": tmp.get("ctime"),
                "委托类型": tmp.get("type"),
                "委托方向": tmp.get("side"),
                "价格": tmp.get("price"),
                "委托数量": tmp.get("number"),
                "委托总额": tmp.get("total_price"),
                "已成交数量": tmp.get("deal_number"),
                "已成交均价": tmp.get("deal_price"),
                "状态": tmp.get("status"),

            }
            result.append(data_template)
        return result

    # 查询我的资产 https://aofex.zendesk.com/hc/zh-cn/articles/360036235713-%E6%88%91%E7%9A%84%E8%B5%84%E4%BA%A7
    def get_my_wallet_list(self,*args,**kwargs):
        self.log.info("查询我的资产")
        """
        currency: 查询指定币种
        show_all: 是否需要全部币种（1：需要，不传则有资产的才有）
        """
        url = URL_HOME + my_wallet_list_url
        data = {
            "currency":kwargs.get("currency",""),
            "show_all":kwargs.get("show_all",1),
        }
        args = dict()
        args['url'] = url
        args['method'] = 'GET'
        args['data'] = dict()
        args['data'] = data
        res = self.get_requests(args)
        result = []
        for tmp in res.get("result", {0: 0}):
            data_template = {
                "币种": tmp.get("currency"),
                "可用": tmp.get("available"),
                "冻结": tmp.get("frozen"),
            }
            result.append(data_template)
        return result

    # 查询委托成交详情 https://aofex.zendesk.com/hc/zh-cn/articles/360036235953-%E5%A7%94%E6%89%98%E6%88%90%E4%BA%A4%E8%AF%A6%E6%83%85
    def get_entrust_detail(self,*args,**kwargs):
        self.log.info("查询委托成交详情")
        """
        order_sn: 订单编号
        :param args:
        :param kwargs:
        :return:
        """
        url = URL_HOME + entrust_detail_url
        data = {
            "order_sn":kwargs.get("order_sn", "000000"),
        }
        args = dict()
        args['url'] = url
        args['method'] = 'GET'
        args['data'] = dict()
        args['data'] = data
        res = self.get_requests(args)
        result = []
        for tmp in res.get("result", {0: 0}):
            data_template = {
                "订单id": tmp.get("order_id"),
                "订单编号": tmp.get("order_sn"),
                "交易对": tmp.get("symbol"),
                "委托时间": tmp.get("ctime"),
                "委托类型": tmp.get("type"),
                "委托方向": tmp.get("side"),
                "价格": tmp.get("price"),
                "委托数量": tmp.get("number"),
                "委托总额": tmp.get("total_price"),
                "已成交数量": tmp.get("deal_number"),
                "已成交均价": tmp.get("deal_price"),
                "状态": tmp.get("status"),

            }
            result.append(data_template)
        return result

    # 撮合挂单 https://aofex.zendesk.com/hc/zh-cn/articles/360035736134-%E6%92%AE%E5%90%88%E6%8C%82%E5%8D%95
    def get_entrust_add(self, *args,**kwargs):
        """
            {
            "errno":	0,
            "errmsg":	"success",
            "result":	{
                "order_sn":	"BL786401542840282676"
                }
            }
            :param symbol:  交易对 如BTC-USDT
            :param type: 订单类型：buy-market：市价买,	sell-market：市价卖,	buy-limit：限价买, sell-limit：限价卖
            :param amount: 限价单表示下单数量，市价买单时表示买多少 钱(usdt)，市价卖单时表示卖多少币(btc)
            :param price: 下单价格，市价单不传该参数
            :return:
            """
        url = URL_HOME + entrust_add_url
        data = {
            "symbol":kwargs.get("symbol",""),
            "type":kwargs.get("type",""),
            "amount":kwargs.get("amount",0.0),
            "price":kwargs.get("price",0.0),
        }
        args = dict()
        args['url'] = url
        # args['method'] = 'POST'
        args['method'] = 'POST'
        args['data'] = data
        res = self.get_requests(args)
        return res

    # 撮合挂单
    def get_buy(self):
        self.log.info("撮合挂单")
        a = ccxt.aofex()
        a.apiKey = self._token_
        a.secret = self._secret_key_
        # a.create_limit_buy_order("BTC-USDT",1,8000)
        a.create_limit_buy_order("BTC/USDT",0,0)

    # 取消挂单
    def get_cancel(self):
        self.log.info("取消挂单")
        a = ccxt.aofex()
        a.apiKey = self._token_
        a.secret = self._secret_key_
        # a.create_limit_buy_order("BTC-USDT",1,8000)
        a.cancel_order("","BTC/USDT")



if __name__ == '__main__':
    obj = Market_Trade(URL_HOME, TOKEN, SECRET)
    # 获取交易对列表
    res = obj.get_market_symbols_url()
    print(res)
    # 市场成交价
    res = obj.get_market_trade()
    print(res)
    # # 查询当前委托列表
    res = obj.get_entrust_current_list()
    print(res)
    # # 查询历史委托列表
    res = obj.get_entrust_history_list()
    print(res)
    # # 查询我的资产
    res = obj.get_my_wallet_list()
    print(res)
    # # # 查询委托成交详情
    res = obj.get_entrust_detail()
    print(res)
    # res = obj.get_entrust_add()
    # print(res)
    # obj.get_buy()
    #
    # obj.get_cancel()