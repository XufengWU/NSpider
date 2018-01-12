# -*- coding:utf-8 -*-
import common_news_spider
import util
import requests
from pyquery import PyQuery as pq
import re

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2832.2 Safari/537.36'}
complete_pattern = re.compile(ur'http://.+')


class SpiderLocalpress(common_news_spider.CommonNewsSpider):

    def send_request(self, task):
        r = requests.get(task.url, headers=headers, timeout=self.RESPONSE_TIMEOUT_VALUE)
        task.fetched_at = util.get_now()
        return r

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = doc('main time.updated').attr('datetime')
                t_stamp = util.get_timestamp_from_string(t)
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if not reg_pattern.match(doc_url):
                    return True
                t = doc('main time.updated').attr('datetime')
                t_stamp = util.get_timestamp_from_string(t)
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = doc('h1').text()
        t = doc('main time.updated').attr('datetime')
        t_stamp = util.get_timestamp_from_string(t)
        category = doc('.entry-category a').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, 'main .entry-content p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'LocalPress'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        localpress_seed = {'http://www.localpresshk.com/'}
        try:
            r = requests.get('http://www.localpresshk.com/', headers=headers)
            d = pq(r.text)
            for a in d('.menu-newss-container a').items():
                if a.attr('href') and complete_pattern.match(a.attr('href')):
                    localpress_seed.add(a.attr('href'))
        except Exception, e:
            raise e
        day_str = util.get_day_string('/', offset=offset)
        day_str = day_str[:-3]
        spider_localpress = SpiderLocalpress('SpiderLocalpress',
                                             localpress_seed,
                                             {ur'http://www.localpresshk.com/' + day_str + '.+'},
                                             THREAD_NUM=5)
        spider_localpress.OFFSET = offset
        spider_localpress.BATCH_NUMBER = util.get_day_stamp() + 10390
        return spider_localpress


if __name__ == '__main__':
    SpiderLocalpress.PUT_IN_STORAGE = False
    SpiderLocalpress.start_crawling()
