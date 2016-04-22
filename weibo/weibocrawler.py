__author__ = 'Administrator'

import http.cookiejar
import urllib.request
from urllib.error import *
import urllib.parse
import json
from bs4 import BeautifulSoup
import re
import redis
import os

from time import sleep, localtime, strftime
from weibo.models import WeiboUser, Blog, Comment, Fans


class WeiboCrawler:
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.opener = self.make_my_opener()
        self.index = 0
        self.login_url = 'https://passport.weibo.cn/sso/login'
        self.proxies = [{"HTTP": "58.248.137.228:80"}, {"HTTP": "58.251.132.181:8888"}, {"HTTP": "60.160.34.4:3128"},
                        {"HTTP": "60.191.153.12:3128"}, {"HTTP": "60.191.164.22:3128"}, {"HTTP": "80.242.219.50:3128"},
                        {"HTTP": "86.100.118.44:80"}, {"HTTP": "88.214.207.89:3128"}, {"HTTP": "91.183.124.41:80"},
                        {"HTTP": "93.51.247.104:80"}]
        self.head = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Host': 'm.weibo.cn',
            'Proxy-Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'
        }
        self.TRY_TIMES = 10
        self.SLEEP_TIME = 5
        self.user_id = None
        self.stage_id = None
        # self.seed = 'http://m.weibo.cn/login?ns=1&backURL=http%3A%2F%2Fm.weibo.cn%2F&backTitle=%CE%A2%B2%A9&vt=4&'

    def change_proxy(self):
        proxy_handler = urllib.request.ProxyHandler(self.proxies[self.index % self.proxies.__len__()])
        print("换代理了..."+str(self.proxies[self.index % self.proxies.__len__()]))
        self.index += 1
        if self.index >= 1000:
            self.index = 0
        # proxy_auth_handler = urllib.request.ProxyBasicAuthHandler()

        self.opener.add_handler(proxy_handler)

    def login(self):
        args = {
            'username': '767543579@qq.com',
            'password': 'QWErty',
            'savestate': 1,
            'ec': 0,
            'pagerefer': 'https://passport.weibo.cn/signin/'
                         'welcome?entry=mweibo&r=http%3A%2F%2Fm.weibo.cn%2F&wm=3349&vt=4',
            'entry': 'mweibo',
            'wentry': '',
            'loginfrom': '',
            'client_id': '',
            'code': '',
            'qq': '',
            'hff': '',
            'hfp': ''
        }

        post_data = urllib.parse.urlencode(args).encode()
        try:
            self.opener.open(self.login_url, post_data)
            print("login successful")
        except Exception:
            print("login failed")
        self.change_header()
        uid_re = re.compile('"uid":"(.*?)"')
        sid_re = re.compile("\'stageId\':\'(.*?)\'")
        rsp = self.opener.open('http://m.weibo.cn/')
        find = uid_re.findall(rsp.read().decode())
        self.user_id = find[0]
        rsp = self.opener.open('http://m.weibo.cn/u/'+self.user_id)
        find = sid_re.findall(rsp.read().decode())
        self.stage_id = str(find[0])
        # html = BeautifulSoup(rsp.read().decode())
        print('stage'+self.stage_id)
        print('uid'+self.user_id)



    def make_my_opener(self):
        """
        模拟浏览器发送请求
        :return:
        """
        head = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Connection': 'keep-alive',
            'Content-Length': '254',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'passport.weibo.cn',
            'Origin': 'https://passport.weibo.cn',
            'Referer': 'https://passport.weibo.cn/signin/login?'
                       'entry=mweibo&res=wel&wm=3349&r=http%3A%2F%2Fm.weibo.cn%2F',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML,'
                          ' like Gecko) Chrome/37.0.2062.124 Safari/537.36'
        }
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        header = []
        for key, value in head.items():
            elem = (key, value)
            header.append(elem)
        opener.addheaders = header
        return opener

    def change_header(self):
        head = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip,deflate,sdch',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Host': 'm.weibo.cn',
            # 'Referer': 'http://m.weibo.cn/page/tpl?containerid='+str(self.stage_id)+'_-_WEIBO_SECOND_PROFILE_WEIBO',
            'Proxy-Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'
        }
        if self.stage_id is not None:
            head['Referer'] = 'http://m.weibo.cn/page/tpl?containerid='+str(self.stage_id)+\
                              '_-_WEIBO_SECOND_PROFILE_WEIBO'
        header = []
        for key, value in head.items():
            elem = (key, value)
            header.append(elem)
        self.opener.addheaders = header

    def insert_blog_info(self, blog_info):
        # print('insert blog info '+str(blog_info))
        if blog_info.__contains__('deleted'):
            return
        blog_id = blog_info['idstr']

        blog_text = blog_info['text']
        blog_source = blog_info['source']

        blog_created_timestamp = blog_info['created_timestamp']

        blog_create_at = strftime('%Y-%m-%d %H:%M:%S', localtime(int(blog_created_timestamp)))
        blog_like_count = blog_info['like_count']
        blog_comment_count = blog_info['comments_count']
        blog_forward_conut = blog_info['attitudes_count']  # TODO
        blog_pic_ids = ''
        if blog_info.__contains__('pics'):
            blog_pictures = blog_info['pics']

            for pic in blog_pictures:
                self.insert_pic_info(pic)
                blog_pic_ids += pic['pid']+','
        blog_retweet_id = ''
        if blog_info.__contains__('retweeted_status'):
            self.insert_blog_info(blog_info['retweeted_status'])
            blog_retweet_id += blog_info['retweeted_status']['idstr']
        if self.insert_user_info(blog_info['user']):
            try:
                blog = Blog.objects.get(blog_id=blog_id)
            except Blog.DoesNotExist:
                blog = Blog()
            blog.blog_id = blog_id
            blog.text = blog_text
            blog.source = blog_source
            blog.created_at = blog_create_at
            blog.created_timestamp = blog_created_timestamp
            blog.like_count = blog_like_count
            blog.comment_count = blog_comment_count
            blog.forward_count = blog_forward_conut
            blog.retweet_id = blog_retweet_id
            blog.user_id = blog_info['user']['id']
            blog.save()
        # 获取评论
        self.grab_comment(blog_id)

    def insert_pic_info(self, pic_info):
        pic_id = pic_info['pid']
        pic_url = pic_info['url']
        # self.mysqlconn.execute_single(self.pic_insert_query, (pic_id, pic_url))
        pass

    def insert_user_info(self, user_info):
        # print("user info "+str(user_info))
        address_re = re.compile('.*<div class="item-info-page"><span>所在地</span><p>(.*?)</p></div>.*')
        gender_re = re.compile('.*<div class="item-info-page"><span>性别</span><p>(.*?)</p></div>.*')
        email_re = re.compile('.*<div class="item-info-page"><span>邮箱</span><p>(.*?)</p></div>.*')
        edu_re = re.compile('.*<div class="item-info-page"><span>大学</span><p>(.*?)</p><p>(.*?)</p><p>(.*?)</p></div>.*')

        user_id = user_info['id']
        if user_id is None:
            return False
        try:
            user = WeiboUser.objects.get(user_id=user_id)
        except WeiboUser.DoesNotExist:
            user = WeiboUser()
        user.user_id = str(user_id)
        rsp = self.opener.open('http://m.weibo.cn/users/'+str(user_id)+'?')
        html = rsp.read().decode()
        address = address_re.match(html)
        if address:
            user.address = address.group(1)
        gender = gender_re.match(html)
        if gender:
            user.gender = gender.group(1)
        email = email_re.match(html)
        if email:
            user.email = email.group(1)
        edu = edu_re.match(html)
        if edu:
            user.edu_info = edu.group(1)
        user.description = str(user_info['description'])
        user.fans_num = str(user_info['fansNum'])
        user.screen_name = user_info['screen_name']
        user.statuses_count = str(user_info['statuses_count'])
        user.follow_num = '0'  # user_info['follow_num']
        user.profile_image_url = user_info['profile_image_url']
        user.profile_url = user_info['profile_url']
        user.save()
        return True

    def insert_comment_info(self, comment_info):
        print(comment_info)
        comment_id = comment_info['id']
        try:
            comment = Comment.objects.get(comment_id=comment_id)
        except Comment.DoesNotExist:
            comment = Comment()
        comment.comment_id = comment_id
        comment.created_at = comment_info['created_at']
        comment.like_counts = str(comment_info['like_counts'])
        comment.blog_id = comment_info['blog_id']
        comment.text = comment_info['text']
        comment.user_id = comment_info['user']['id']  # TODO
        comment.save()
        pass

    def grab_user_blogs(self):
        error = False
        page = 1
        url = 'http://m.weibo.cn/page/json?containerid='+str(self.stage_id)+'_-_WEIBO_SECOND_PROFILE_WEIBO' \
                                                                            '&page='+str(page)
        print("正在打开："+url)
        rsp = self.opener.open(url)
        return_json = json.loads(rsp.read().decode())
        print('返回数据：'+str(return_json))
        card = return_json['cards'][0]
        max_page = card['maxPage']
        card_group = card['card_group']
        for blog_info in card_group:
            if blog_info['card_type'] != 9:
                continue
                # print(blog_info['mblog'])
            self.insert_blog_info(blog_info['mblog'])
        page += 1

        while page <= max_page:
            url = 'http://m.weibo.cn/page/json?containerid='+str(self.stage_id)+'-_WEIBO_SECOND_PROFILE_WEIBO&' \
                                                                                'page='+str(page)
            print("正在打开："+url)
            rsp = self.opener.open(url)
            return_json = json.loads(rsp.read().decode())
            print('返回数据：'+str(return_json))
            cards = return_json['cards']

            for card in cards:
                if card.__contains__('msg'):
                    error = True
                    break
                card_group = card['card_group']
                error = False
                for blog_info in card_group:
                    if blog_info['card_type'] != 9:
                        continue
                    # print(blog_info['mblog'])
                    self.insert_blog_info(blog_info['mblog'])
            if not error:
                page += 1
            sleep(self.SLEEP_TIME)
            self.change_proxy()

    def start(self):
        self.login()
        self.grab_user_blogs()
        # self.grab_fans(self.user_id)
        # self.mysqlconn.close()
        #
        # self.save_pic()

    def save_pic(self):
        url = 'http://ww2.sinaimg.cn/large/c0788b86jw1f2xfstebzaj20dc0hst9r.jpg'
        rsp = self.opener.open(url)
        pic_data = rsp.read()
        try:
            file = open("d:\\weibo_pic\\1.jpg", 'wb')
            file.write(pic_data)
            file.close()
        except FileNotFoundError:
            os.mkdir("d:\\weibo_pic")
        except FileExistsError:
            pass

    def get_comment_by_page(self, blog_id, page_num):
        url = 'http://m.weibo.cn/single/rcList?format=cards&id='
        req_url = url + str(blog_id) + '&type=comment&hot=0&page='+str(page_num)
        print('浏览器正在打开url：'+req_url)
        rsp = None
        time = 0
        while time <= self.TRY_TIMES:
            try:
                rsp = self.opener.open(req_url)
                break
            except HTTPError as e:
                sleep(10)
                time += 1
                print(e)
                print('try time:'+str(time))
        if rsp is None:
            print('can\'t open url'+req_url)
            return
        return_json = json.loads(rsp.read().decode())
        print('请求返回数据:\t'+str(return_json))
        if page_num == 1:
            comment_json = return_json[1]
        else:
            comment_json = return_json[0]
        return comment_json

    def grab_comment(self, blog_id):
        page = 1
        comment_json = self.get_comment_by_page(blog_id, page)
        print('评论——json\t' + str(comment_json))
        if 'maxPage' not in comment_json:
            return
        max_page = comment_json['maxPage']
        page += 1
        if 'card_group' in comment_json:
            comment_card_group = comment_json['card_group']
            for comment_group in comment_card_group:
                comment_group['blog_id'] = blog_id
                self.insert_comment_info(comment_group)
                # self.print_comment(comment_group)
        print("总页面数：max_page：\t"+str(max_page))
        while page <= max_page:
            print("curr_page:\t"+str(page)+"\t    max_page\t:"+str(max_page))
            comment_json = self.get_comment_by_page(blog_id, page)
            if 'card_group' in comment_json:
                comment_card_group = comment_json['card_group']
                for comment_group in comment_card_group:
                    comment_group['blog_id'] = blog_id
                    self.insert_comment_info(comment_group)
                    # self.print_comment(comment_group)
            page += 1
            sleep(self.SLEEP_TIME)
            self.change_proxy()

    def grab_weibo(self):
        open_url = 'http://m.weibo.cn/index/feed?format=cards'
        print('浏览器正在打开url：' + open_url)
        rsp = None
        try_time = 0
        while try_time <= self.TRY_TIMES:
            try:
                rsp = self.opener.open(open_url)
                break
            except HTTPError as e:
                sleep(self.SLEEP_TIME)
                try_time += 1
                print(e)
                print('try time:'+str(try_time))
        if rsp is None:
            print('failed open url:'+open_url)
            return
        return_json = json.loads(rsp.read().decode())
        card_group = return_json[0]['card_group']
        next_cursor = return_json[0]['next_cursor']
        previous_cursor = return_json[0]['previous_cursor']
        page = return_json[0]['page']
        max_page = return_json[0]['maxPage']
        page = 1

        c = '3963770537235924&type=comment&hot=0&page=2'
        for group in card_group:
            # self.print_info(group)
            mblog = group['mblog']
            curr_blog_id = mblog['id']
            user = mblog['user']
            user_id = user['id']
            self.grab_comment(curr_blog_id)
            # page += 1

        n = 20
        while n > 0:
            self.change_proxy()
            n -= 1
            open_url = 'http://m.weibo.cn/index/feed?format=cards&next_cursor='+str(next_cursor) + '&page='+str(page)
            print('浏览器正在打开url：' + open_url)
            rsp = self.opener.open(open_url)
            return_json = json.loads(rsp.read().decode())
            card_group = return_json[0]['card_group']
            next_cursor = return_json[0]['next_cursor']
            previous_cursor = return_json[0]['previous_cursor']
            for group in card_group:
                # self.print_info(group)
                mblog = group['mblog']
                curr_blog_id = mblog['id']
                user = mblog['user']
                user_id = user['id']
                self.grab_comment(curr_blog_id)
        return

    def grab_fans(self, user_id):
        page = 0
        seed_url = 'http://m.weibo.cn/page/json?containerid=100505'+str(user_id)+'_-_FANS&page='
        print(seed_url+str(page))
        rsp = self.opener.open(seed_url+str(page))
        return_json = json.loads(rsp.read().decode())
        max_page = 1
        cards = return_json['cards']
        count = 0
        print('----cards--'+str(cards))
        for card in cards:
            print('card' + str(card))
            max_page = card['maxPage']
            if card.__contains__('card_group'):
                card_group = card['card_group']
                count += card_group.__len__()
                print(card_group.__len__())
                for c in card_group:
                    follower = c['user']['id']
                    exist = Fans.objects.filter(user_id=follower).filter(follow_user_id=user_id)
                    if not exist:
                        fans = Fans()
                        fans.follow_user_id = user_id
                        fans.user_id = c['user']['id']
                        fans.save()
                        print(c['user']['screen_name'])
        page += 1
        while page <= max_page:
            rsp = self.opener.open(seed_url+str(page))
            return_json = json.loads(rsp.read().decode())
            cards = return_json['cards']
            for card in cards:

                if card.__contains__('card_group'):
                    card_group = card['card_group']
                    count += card_group.__len__()
                    print(card_group.__len__())
                    for c in card_group:
                        follower = c['user']['id']
                        exist = Fans.objects.filter(user_id=follower).filter(follow_user_id=user_id)

                        if not exist:
                            fans = Fans()
                            fans.follow_user_id = user_id
                            fans.user_id = c['user']['id']
                            fans.save()
                            # print(c['user']['screen_name'])

            page += 1
        # print(count)


def main():
    my = WeiboCrawler("", "")
    my.start()

if __name__ == '__main__':
    main()
