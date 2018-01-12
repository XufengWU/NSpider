# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import urllib2
import time
import threading
import requests
from pyquery import PyQuery as pq
import gc


domain_prefix = u'http://hd.stheadline.com'
complete_pattern = re.compile(ur'http://.+')
year_date_pattern = re.compile(str(time.localtime().tm_year) + r'\d\d\d\d')
ip_pattern = re.compile(ur'\d+\.\d+\.\d+\.\d')
proxy_turn_lock = threading.Lock()
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'hd.stheadline.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}


def get_proxies_list():
    print 'Using proxies.'
    _ips = set()
    start_pages = {'http://proxy.com.ru/niming/',
                   'http://proxy.com.ru/gaoni/'}
    for page in start_pages:
        print '**** New IPs: ****'
        ips = set()
        r = requests.get(page)
        r.encoding = 'gb2312'
        d = pq(r.text)
        for tr in d('tr').items():
            if ip_pattern.match(tr('td:nth-child(3)').text()) and (
                    tr('td:nth-child(4)').text() == '80' or tr('td:nth-child(4)').text() == '8080'):
                print tr('td:nth-child(3)').text() + ':' + tr('td:nth-child(4)').text()
                ips.add(tr('td:nth-child(3)').text() + ':' + tr('td:nth-child(4)').text())
        print '**** Checking IPs: ****'
        for ip in ips:
            url = u'http://www.google.com'
            proxies = {'http': ip}
            proxy_support = urllib2.ProxyHandler(proxies)  # register a proxy
            opener = urllib2.build_opener(proxy_support)
            good = True
            try:
                opener.open(url, timeout=5)
            except Exception, e:
                good = False
                print ip + " " + str(e)
                pass
            if good:
                _ips.add(ip)
        print '**** Valid IPs: ****'
        for ip in _ips:
            print ip
    return list(_ips)


class SpiderHeadline(common_news_spider.CommonNewsSpider):

    ips = None
    turn = 0
    using_proxy = True

    def send_request(self, task):
        task.fetched_at = util.get_now()
        if self.using_proxy:
            with proxy_turn_lock:
                proxies = {'http': self.ips[self.turn]}
                self.turn += 1
                if self.ips.__len__() <= self.turn:
                    self.turn = 0
            r = requests.get(url=task.url, timeout=self.RESPONSE_TIMEOUT_VALUE, headers=headers, proxies=proxies)
            return r
        r = requests.get(task.url, timeout=self.RESPONSE_TIMEOUT_VALUE)
        return r

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = domain_prefix + u
        else:
            u = ''
        return u

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if doc('time') or doc('span.date'):
                    t = util.get_time_string_from_selectors(doc, {'time', 'span.date'})
                    t_stamp = util.get_timestamp_from_string(t)
                    if t_stamp >= util.get_day_stamp(self.OFFSET):
                        return True
                    return False
                return False
        return False

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if year_date_pattern.findall(url):
                    t = year_date_pattern.findall(url)[0]
                    t_stamp = util.get_timestamp_from_string(t)
                else:
                    if doc('time') or doc('span.date'):
                        t = util.get_time_string_from_selectors(doc, {'time', 'span.date'})
                        t_stamp = util.get_timestamp_from_string(t)
                    else:
                        return True
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, ur' - .*')
        t = ''
        t_stamp = 0
        if doc('time') or doc('span.date'):
            t = util.get_time_string_from_selectors(doc, {'time', 'span.date'})
            t_stamp = util.get_timestamp_from_string(t) + int(time.localtime().tm_sec)
        category = re.sub(ur'.*\s+', u'', doc('.dropdown-menu li.active a').text())
        author = ''
        content = util.get_paragraphs_from_selector(doc, '#news-content')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, '.content span')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'HeadlineNews'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.content .item img').items():
            if img.attr('src') != '':
                media_u = img.attr('src')
                if re.match(r'//.+', media_u):
                    media_u = 'http:' + media_u
                des = ''
                if img.attr('alt'):
                    des = img.attr('alt')
                media = self.NewsItem.MediaItem(media_url=media_u, type='image', description=des,
                                                created_at=item.fetched_at)
                item.media_list.append(media)
        for a in doc('iframe').items():
            if a.attr('src') and re.match(r'.*youtube\.com.+', a.attr('src')):
                media_u = a.attr('src')
                if re.match(r'//.+', media_u):
                    media_u = 'http:' + media_u
                media = self.NewsItem.MediaItem(media_url=media_u, type='youtube', description='youtube',
                                                created_at=item.fetched_at)
                item.media_list.append(media)
        if util.within_active_interval(12, 600):
            _comments = util.get_filtered_facebook_comments_data('978368502211772',
                                                                 doc('div.fb-comments').attr('data-href'), task.url)
            if _comments:
                for _comment in _comments:
                    item.media_list.append(
                        self.NewsItem.MediaItem(media_url=_comment['json_string'], type='comments',
                                                description='comments', created_at=item.fetched_at)
                    )

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        headline_seed = {'http://hd.stheadline.com/', 'http://hd.stheadline.com/news/daily/'}
        # util.add_hrefs(url='http://hd.stheadline.com/', selectors={'ul.list-nav a'},
        #               seeds=headline_seed, prefix=domain_prefix)
        # util.add_hrefs(url='http://hd.stheadline.com/', selectors={'.heading a'},
        #               seeds=headline_seed, prefix=domain_prefix)
        spider_headline = SpiderHeadline('SpiderHeadline',
                                         headline_seed,
                                         {ur'http://hd\.stheadline\.com/news/(?!columns).+/\d+.*',
                                          ur'http://hd\.stheadline\.com/news/columns/\d+/\d+.*'},
                                         THREAD_NUM=1, MAX_DEPTH=5)
        spider_headline.FETCH_DELAY = 15
        spider_headline.RETRY_TIMES = 3
        spider_headline.RESPONSE_TIMEOUT_VALUE = 10
        spider_headline.using_proxy = False
        # spider_headline.ips = get_proxies_list()
        # spider_headline.turn = random.randint(0, len(spider_headline.ips)-1)
        # spider_headline.THREAD_NUM = len(spider_headline.ips)
        spider_headline.BATCH_NUMBER = util.get_day_stamp() + 10160
        spider_headline.OFFSET = offset
        spider_headline.ADD_MEDIA = True
        return spider_headline


if __name__ == '__main__':

    SpiderHeadline.PUT_IN_STORAGE = True
    while True:
        SpiderHeadline.start_crawling()
        gc.collect()
        time.sleep(5 * 60)
