# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import requests
from pyquery import PyQuery as pq

complete_pattern = re.compile(ur'http://.+')
news_prefix = 'http://cn.wsj.com/gb/'
incomplete_cat_url_pattern = re.compile(ur'^\./.+\.asp')
date_patterns = {re.compile(ur'\d{4}年\d\d月\d\d日 \d\d:\d\d')}
seed_patterns = {re.compile(r'(?<=\./).+\.asp')}
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2832.2 Safari/537.36'}


class SpiderWSJ(common_news_spider.CommonNewsSpider):

    def send_request(self, task):
        r = requests.get(task.url, headers=headers, timeout=self.RESPONSE_TIMEOUT_VALUE)
        task.fetched_at = util.get_now()
        return r

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = news_prefix + u
        else:
            u = ''
        return u

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1'})
        t = util.get_time_string_from_selectors(doc, {'time.timestamp'})
        t_stamp = util.get_timestamp_from_string(t)
        cat = doc('body').attr('class')
        category = ''
        if doc('.article-breadCrumb a'):
            category = doc('.article-breadCrumb a').text()
        author = doc('.author span').text()
        content = util.get_paragraphs_from_selector(doc, '#A p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'WSJ'
        item.task_no = self.BATCH_NUMBER
        for img in doc('#A .media-object-image img').items():
            if img.attr('src') != '':
                media_u = img.attr('src')
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

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        _wsj_seed = {'http://cn.wsj.com/gb/globe.asp'}
        util.add_hrefs('http://cn.wsj.com/gb/globe.asp', {'#navigation a[target=_top]'}, _wsj_seed)
        wsj_seed = set()
        for url in _wsj_seed:
            if incomplete_cat_url_pattern.match(url):
                url = news_prefix + url[2:]
                wsj_seed.add(url)
        day_str = util.get_day_string(offset=offset)
        spider_wsj = SpiderWSJ('SpiderWSJ',
                               wsj_seed,
                               {ur'http://cn.wsj.com/gb.+' + day_str + '.+'},
                               THREAD_NUM=5)
        spider_wsj.OFFSET = offset
        spider_wsj.BATCH_NUMBER = util.get_day_stamp() + 10380
        return spider_wsj

if __name__ == '__main__':
    SpiderWSJ.PUT_IN_STORAGE = False
    SpiderWSJ.start_crawling()
