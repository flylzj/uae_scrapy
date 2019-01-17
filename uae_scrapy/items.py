# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UaeScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class OrderItem(scrapy.Item):
    item_type = "order"
    order_id = scrapy.Field()
    SKU = scrapy.Field()
    EAN = scrapy.Field()
    QTY = scrapy.Field()
    order_date = scrapy.Field()
    status = scrapy.Field()
    net_total = scrapy.Field()
    item_title = scrapy.Field()
    item_detail = scrapy.Field()


class TotalOrderItem(scrapy.Item):
    item_type = "total"
    date = scrapy.Field()
    order_id = scrapy.Field()
    status = scrapy.Field()
    debit = scrapy.Field()
    credit = scrapy.Field()
    balance = scrapy.Field()

