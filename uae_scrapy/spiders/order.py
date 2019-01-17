# -*- coding: utf-8 -*-
import scrapy
import re
import json
from uae_scrapy.items import OrderItem


class OrderSpider(scrapy.Spider):
    name = 'order'
    allowed_domains = ['souq.com', 'amazon.co.uk']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0"
    }
    token = ""
    order_info_url = 'https://mobileapi.souq.com/v1/products/{}' \
                     '?city_id=&show_attributes=1&show_offers=1&show_variations=1&country=sa&' \
                     'language=en&format=json&app_id=61506485&app_secret=Fh6Q9BRCpNTlLcnEqHNV&' \
                     'platform=ANDROID&c_ident=14981909405422&signature=b4f9d2aef9acfd8dcb80da25b67d7881'

    config = {}

    def get_config(self):
        with open("config.json", encoding="utf-8") as f:
            return json.load(f)

    def make_headers(self, dic=None):
        h = self.headers.copy()
        if dic:
            h.update(dic)
        return h

    def start_requests(self):
        self.config = self.get_config()
        login_url_1 = "https://uae.souq.com/ae-en/auth_portal.php"
        username, password = self.config.get("username"), self.config.get("password")
        info = {
            "login_url_1": login_url_1,
            "username": username,
            "password": password,
        }
        self.logger.info("*************************")
        for k, v in self.config.items():
            self.logger.info("*****{}: {}".format(k, v))
        self.logger.info("*************************")
        yield scrapy.Request(login_url_1, meta=info, callback=self.loing2)

    def loing2(self, response):
        hitsCfs_pattern =\
            r'<input.*name="hitsCfs".*value="(.*)"[\s\S]+<input.*name="hitsCfsMeta".*value="(.*)".*/><input'
        compile = re.compile(hitsCfs_pattern)
        result = compile.search(response.text)
        if result:
            r = result.groups()
            meta = response.meta
            meta["hitsCfs"] = r[0]
            meta["hitsCfsMeta"] = r[1]
            data = {
                "action": "auth_portal_login",
                "ajax": "authPortalLogin",
                "email": meta.get("username")
            }
            yield scrapy.FormRequest(meta.get("login_url_1"), formdata=data, meta=meta, callback=self.login3)

    def login3(self, response):
        login_url_2 = json.loads(response.text).get("aData").get("redirectLink")
        meta = response.meta
        meta["login_url_2"] = login_url_2
        dic = {
            "Referer": "https://uae.souq.com/ae-en/auth_portal.php?action=index"
        }
        yield scrapy.Request(login_url_2, headers=self.make_headers(dic), meta=meta, callback=self.login4)

    def login4(self, response):
        appActionToken_pattern = \
            r'<input.*name="appActionToken".*value="(.*)".*/><'
        appAction_pattern = \
            r'<input.*name="appAction".*value="(.*)".*/>'
        openidreturn_to_pattern = \
            r'<input.*name="openid.return_to".*value="(.*)".*/>'
        prevRID_pattern = \
            r'<input.*name="prevRID".*value="(.*)".*/>'
        workflowState_pattern = r'<input.*name="workflowState".*value="(.*)".*/>'

        meta = response.meta
        metadata1_pattern = r''
        # amazonCID_pattern = \
        #     r'<input.*name="amazonCID".*value="(.*)".*>'

        appActionToken = re.compile(appActionToken_pattern).search(response.text).groups()[0] if \
            re.compile(appActionToken_pattern).search(response.text) else \
            ""
        appAction = re.compile(appAction_pattern).search(response.text).groups()[0] if \
            re.compile(appAction_pattern).search(response.text) else \
            ""
        openidreturn_to = re.compile(openidreturn_to_pattern).search(response.text).groups()[0] if \
            re.compile(openidreturn_to_pattern).search(response.text) else \
            ""
        prevRID = re.compile(prevRID_pattern).search(response.text).groups()[0] if \
            re.compile(prevRID_pattern).search(response.text) else \
            ""
        workflowState = re.compile(workflowState_pattern).search(response.text).groups()[0]if \
            re.compile(workflowState_pattern).search(response.text) else \
            ""
        data = {
            "appActionToken": appActionToken,
            "appAction": appAction,
            "openid.return_to": openidreturn_to,
            "prevRID": prevRID,
            "workflowState": workflowState,
            "email": meta["username"],
            "password": "",
            "create": "0",
            "metadata1": ""
        }
        yield scrapy.FormRequest("https://www.amazon.co.uk/ap/signin", formdata=data, meta=meta, callback=self.login5)

    def login5(self, response):
        appActionToken_pattern = \
            r'<input.*name="appActionToken".*value="(.*)".*/><'
        appAction_pattern = \
            r'<input.*name="appAction".*value="(.*)".*/>'
        openidreturn_to_pattern = \
            r'<input.*name="openid.return_to".*value="(.*)".*/>'
        prevRID_pattern = \
            r'<input.*name="prevRID".*value="(.*)".*/>'
        workflowState_pattern = r'<input.*name="workflowState".*value="(.*)".*/>'

        appActionToken = re.compile(appActionToken_pattern).search(response.text).groups()[0] if \
            re.compile(appActionToken_pattern).search(response.text) else \
            ""
        appAction = re.compile(appAction_pattern).search(response.text).groups()[0] if \
            re.compile(appAction_pattern).search(response.text) else \
            ""
        openidreturn_to = re.compile(openidreturn_to_pattern).search(response.text).groups()[0] if \
            re.compile(openidreturn_to_pattern).search(response.text) else \
            ""
        prevRID = re.compile(prevRID_pattern).search(response.text).groups()[0] if \
            re.compile(prevRID_pattern).search(response.text) else \
            ""
        workflowState = re.compile(workflowState_pattern).search(response.text).groups()[0] if \
            re.compile(workflowState_pattern).search(response.text) else \
            ""
        meta = response.meta

        data = {
            "appActionToken": appActionToken,
            "appAction": appAction,
            "openid.return_to": openidreturn_to,
            "prevRID": prevRID,
            "workflowState": workflowState,
            "metadata1": "",
            "email": meta["username"],
            "password": meta["password"]
        }
        yield scrapy.FormRequest("https://www.amazon.co.uk/ap/signin",
                                 formdata=data,
                                 meta=meta,
                                 callback=self.login_done)

    def login_done(self, response):
        url = "https://sell.souq.com/"
        yield scrapy.Request(url, callback=self.get_token)

    def get_token(self, response):
        my_cookies = ''.join([cookie.decode() for cookie in response.headers.getlist('Set-Cookie')])
        self.logger.info(my_cookies)
        self.token = re.findall('SCXAT=([0-9a-zA-z]*)', my_cookies)
        if self.token:
            self.token = self.token[0]
        else:
            self.token = ""
        self.logger.info('TOKEN')
        self.logger.info(self.token)
        self.logger.info('TOKEN')
        count = int(self.config.get("orders_count"))
        order_interval = self.config.get("order_placed_in")
        url = "https://sell.souq.com/orders/getOrders"
        params = {
            "isFbs": "true",
            "interval": "{}".format(order_interval),
            "orderStatus": "ALL_SHIPMENT",
            "sortKey": "orderDate",
            "sortOrder": "desc",
            "page": 0,
            "size": count + 1000
        }
        yield scrapy.Request(self.make_params_url(url, params), callback=self.get_orders)

    def get_orders(self, response):
        datas = json.loads(response.text).get("data")
        self.logger.info("一共有: {}订单".format(len(datas)))
        for data in datas:
            item_id = data.get("shipmentOrderUnits")
            if item_id:
                item_id = item_id[0].get("idItem")
            else:
                self.logger.info("没有item_id, {}".format(str(data)))
                continue
            order_item = OrderItem()
            order_item["order_id"] = data.get("orderIdStr")
            order_item["order_date"] = data.get("orderDate")
            order_item["SKU"] = data.get("unitSKUs")
            order_item["QTY"] = data.get("quantity")
            order_item["status"] = data.get("shipmentStatus")[0] if data.get("shipmentStatus") else ""
            order_item["net_total"] = data.get("grandTotal") / 100
            order_item["item_detail"] = [
                data.get("subTotal") / 100,
                data.get("commisionFees") / 100,
                data.get("closingFee") / 100,
                data.get("easyShipFee") / 100,
                data.get("fbaFee") / 100,
                data.get("referalFee") / 100,
                data.get("grandTotal") / 100
            ]
            yield scrapy.Request(self.order_info_url.format(item_id),
                                 callback=self.get_order_detail,
                                 dont_filter=True,
                                 meta={"order_item": order_item})

    def get_order_detail(self, response):
        order_item = response.meta["order_item"]
        data = json.loads(response.text).get("data")
        order_item["EAN"] = data.get("ean")[0] if data.get("ean") else ""
        order_item["item_title"] = data.get("label")
        yield order_item

    def make_params_url(self, url, params):
        url += "?"
        ps = []
        for k, v in params.items():
            ps.append("{}={}".format(k, v))

        url += "&".join(ps)
        return url



