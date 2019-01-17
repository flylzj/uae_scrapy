# -*- coding: utf-8 -*-
import time
import csv
import re
import os


class UaeScrapyPipeline(object):
    def __init__(self):
        self.clear_csv()
        self.order_writer = self.get_writer("order")
        self.total_writer = self.get_writer('total')
    #     self.order_writer = self.get_writer("order")
    #     self.total_writer = self.get_writer("total")

    def process_item(self, item, spider):
        if item.item_type == "order":
            self.deal_order_item(item)
        elif item.item_type == "total":
            self.deal_total_order_item(item)
        return item

    def clear_csv(self):
        try:
            os.remove("order.csv")
            print("rm order.csv")
        except Exception as e:
            pass
        try:
            os.remove("total.csv")
            print("rm total.csv")
        except Exception as e:
            pass

    def deal_order_item(self, item):
        item["order_date"] = self.convert_order_date(item["order_date"])
        self.order_writer.writerow(
                [
                    str(item["order_id"]) + "\t",
                    item["SKU"],
                    str(item["EAN"]) + "\t",
                    item["QTY"],
                    item["order_date"],
                    item["status"],
                    item["net_total"],
                    item["item_title"],
                    item["item_detail"][0],
                    item["item_detail"][1],
                    item["item_detail"][2],
                    item["item_detail"][3],
                    item["item_detail"][4],
                    item["item_detail"][5],
                    item["item_detail"][6],
                ]
            )
        return item

    def deal_total_order_item(self, item):
        item["status"] = re.search(r'(Payment|Release|Returned|Cancellation)', item["status"]).group() if \
            re.search(r'(Payment|Release|Returned|Cancellation)', item["status"]) else ""
        self.total_writer.writerow(
            [
                item["date"],
                str(item["order_id"]) + "\t",
                item["status"],
                item["debit"],
                item["credit"],
                item["balance"]
            ]
        )
        return item

    def convert_order_date(self, order_date):
        d = time.ctime(order_date//1000).split()
        return "{} {}, {}".format(d[1], d[2], d[-1])

    def get_writer(self, item_type):
        if item_type == "order":
            writer = csv.writer(open("order.csv", "a+", encoding="utf-8", newline=""))
            writer.writerow(
                [
                    "order_id",
                    "SKU",
                    "EAN",
                    "QTY",
                    "order_date",
                    "status",
                    "net_total",
                    "item_title",
                    "subTotal",
                    "commisionFees",
                    "closingFee",
                    "easyShipFee",
                    "fbaFee",
                    "referalFee",
                    "grandTotal"
                ]
            )
        elif item_type == "total":
            writer = csv.writer(open("total.csv", "a+", encoding="utf-8", newline=""))
            writer.writerow(["date", "order_id", "status", "debit", "credit", "balance"])
        else:
            writer = csv.writer(open("order.csv", "a+", encoding="utf-8", newline=""))
            writer.writerow(
                [
                    "order_id",
                    "SKU",
                    "EAN",
                    "QTY",
                    "order_date",
                    "status",
                    "net_total",
                    "item_title",
                    "subTotal",
                    "commisionFees",
                    "closingFee",
                    "easyShipFee",
                    "fbaFee",
                    "referalFee",
                    "grandTotal"
                ]
            )
        return writer





