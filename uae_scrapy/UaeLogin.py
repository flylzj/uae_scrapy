# coding: utf-8
import requests
import re
import json
import pickle
import logging
import queue
import threading
from requests.adapters import HTTPAdapter


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UaeSpider(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0"
        }
        # 因为登录有两步，先输入账号，跳转到另外一个url输入密码
        self.session = requests.Session()
        self.hitsCfs_pattern =\
            r'<input.*name="hitsCfs".*value="(.*)"[\s\S]+<input.*name="hitsCfsMeta".*value="(.*)".*/><input'
        self.amazonCID_pattern = \
            r'<input.*name="amazonCID".*value="(.*)".*>'
        self.login_url_1 = "https://uae.souq.com/ae-en/auth_portal.php"

    def make_headers(self, dic=None):
        h = self.headers.copy()
        if dic:
            h.update(dic)
        return h

    # 拿到hitsCfs和hitsCfsMeta
    def login1(self, session):
        try:
            r = session.get(self.login_url_1, headers=self.make_headers())
            com = re.compile(self.hitsCfs_pattern)
            result = com.search(r.text)
            if result:
                return result.groups()
        except Exception as e:
            logger.error("login1 err {}".format(e), exc_info=True)
            return None

    # post拿到下一个url
    def login2(self, session, username):
        data = {
            "action": "auth_portal_login",
            "ajax": "authPortalLogin",
            "email": username
        }
        try:
            r = session.post(self.login_url_1, data=data, headers=self.make_headers())
            return r.json().get("aData").get("redirectLink")
        except json.JSONDecodeError as e:
            logger.error("login2 err: {}".format(e), exc_info=True)
        except AttributeError as e:
            logger.error("login2 err: {}".format(e), exc_info=True)
        except Exception as e:
            logger.error("login2 err: {}".format(e), exc_info=True)

    def login3(self, session, login_url):
        try:
            dic = {
                "Referer": "https://uae.souq.com/ae-en/auth_portal.php?action=index"
            }
            r = session.get(login_url, headers=self.make_headers(dic))
            com = re.compile(self.amazonCID_pattern)
            result = com.search(r.text)
            if result:
                return result.groups()[0]
        except Exception as e:
            logger.error("login3 err: {}".format(e), exc_info=True)

    # 登录最后一步
    def login4(self, session, login_url, username, password, hitsCfs=None, hitsCfsMeta=None, amazonCID=None):
        '''
        hitsCfs=d15b0af6e5242a865edb7b27fff9e2d9
        &hitsCfsMeta=SFetb3AR9QrR9HNgm0M%2F9nBnT6JgOwuGy7yt12e4OXB%2FqvSCPUKU4JTjD77enNZiqM8Nklts9RzxQlMyolN9eC7y4n%2FHc%2Fu%2B8nfDfbbWa5vQkYmteBDm8ENxpJJYT3VUYzJefe3O5s6IJd1J1UUeb50PG5rmmE%2B%2BqtmDj%2BYKwT4%3D
        &action=index
        &precautious_login=
        &register_state=1
        &amazonCID=amzn1.application-oa2-client.cd6ef0f2a6aa4abe96070ee6c4cd70c4
        &email=Firecow%40bdtsq.com
        &password=asd123456
        &extended_login=on
        '''

        # 构造登录表单
        data = {
            "hitsCfs": hitsCfs if hitsCfs else "",
            "hitsCfsMeta": hitsCfsMeta if hitsCfsMeta else "",
            "action": "index",
            "precautious_login": "",
            "register_state": 1,
            "amazonCID": amazonCID if amazonCID else 0,
            "emial": username,
            "password": password,
            "extended_login": "on"
        }

        # 构造referer

        dic = {
            "Referer": login_url
        }
        try:
            r = session.post(login_url, data=data, headers=self.make_headers(dic))
            if r.url == "https://uae.souq.com/ae-en/account.php":
                logger.info("登录成功")
                self.save_session(session, username + ".pkl")
            else:
                logger.error("登陆失败")
                exit(1)
        except Exception as e:
            logger.error("登录失败: {}".format(e), exc_info=True)

    # 登录过程
    def login(self, username, password):
        session = self.get_my_session()
        hitsCfs = self.login1(session)
        login_url_2 = self.login2(session, username)
        amazonCID = self.login3(session, login_url_2)
        self.login4(session, login_url_2, username, password, hitsCfs[0], hitsCfs[1], amazonCID)
        return session

    def save_session(self, session, filename):
        try:
            with open(filename, "ab") as f:
                pickle.dump(session, f)
            return True
        except Exception as e:
            return False

    def load_session(self, filename):
        try:
            with open(filename, "rb") as f:
                session = pickle.load(f)
                logger.info("加载上次session成功")
                return session
        except Exception as e:
            logger.error("load session error {}".format(e), exc_info=True)
            return None

    def check_session(self, session):
        url = "https://uae.souq.com/ae-en/account.php"
        try:
            logger.info("正在验证session是否可用")
            r = session.get(url, headers=self.make_headers())
            if r.status_code == 200:
                logger.info("session可用")
                return True
        except Exception as e:
            logger.error("check session error {}".format(e), exc_info=True)
            return False

    def get_session(self, username, password):
        session = self.load_session(username + ".pkl")
        if not session:
            logger.info("加载session失败， 重新登录")
            return self.login(username, password)
        if not self.check_session(session):
            logger.info("session不可用， 重新登录")
            return self.login(username, password)
        return session

    def get_my_session(self):
        session = requests.Session()
        adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session


if __name__ == '__main__':
    username = "Firecow@bdtsq.com"
    password = "asd123456"
    us = UaeSpider()
    us.session = us.get_session(username, password)
    # hitsCfs = us.login1()
    # login_url_2 = us.login2(username)
    # amazonCID = us.login3(login_url_2)
    # us.login4(login_url_2, username, password, hitsCfs[0], hitsCfs[1], amazonCID)