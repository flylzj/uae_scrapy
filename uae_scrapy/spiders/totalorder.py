# -*- coding: utf-8 -*-
import scrapy
import re
import json
from uae_scrapy.items import TotalOrderItem
import time


class TotalorderSpider(scrapy.Spider):
    name = 'totalorder'
    allowed_domains = ['souq.com', 'amazon.co.uk']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0"
    }
    start_urls = ['http://souq.com/']
    config = None
    dates = []

    def get_config(self):
        self.logger.info("正在加载配置")
        with open("config.json", encoding="utf-8") as f:
            return json.load(f)

    def get_date(self):
        try:
            self.dates.append(time.strptime(self.config.get("start_date"), "%d %b, %Y"))
            self.dates.append(time.strptime(self.config.get("end_date"), "%d %b, %Y"))
        except Exception as e:
            self.logger.error("时间配置错误")

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
        url = "https://sell.souq.com/financials/accountSummary?filters%5Btype%5D=pending&acc=pending&page=0&size=20"
        yield scrapy.Request(url, meta={"page": 0, "items_count": 0}, callback=self.get_total_order)

    def get_total_order(self, response):
        meta = response.meta
        page = meta.get("page")
        items_count = meta.get("items_count")
        datas = json.loads(response.text).get("data")
        order_ids = []
        special_order_ids = []
        for data in datas:
            total_order_item = TotalOrderItem()
            total_order_item["date"] = data.get("date")
            order_ids.append(data.get("id_order"))
            if total_order_item["date"] not in self.config.get("total_order_date"):
                continue
            items_count += 1
            self.logger.info("当前订单数量: {}".format(items_count))
            special_order_ids.append(data.get("id_order"))
            total_order_item["order_id"] = data.get("id_order")
            total_order_item["status"] = data.get("text")
            total_order_item["debit"] = data.get("debit")
            total_order_item["credit"] = data.get("credit")
            total_order_item["balance"] = data.get("balance")
            yield total_order_item
        if order_ids[-1] in special_order_ids or (items_count == 0 and len(special_order_ids) == 0):
            self.logger.info("还有数据需要爬取，跳转到下一页")
            url = "https://sell.souq.com/financials/accountSummary?" \
                  "filters%5Btype%5D=pending&acc=pending&page={}&size=20"
            page += 1
            yield scrapy.Request(
                url.format(page),
                meta={"page": page, "items_count": items_count},
                callback=self.get_total_order
            )

