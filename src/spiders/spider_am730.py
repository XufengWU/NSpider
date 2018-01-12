# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time
import threading
import requests
from pyquery import PyQuery as pq


prefix = u'https://theinitium.com'
complete_pattern = re.compile(ur'(http|https)://.+')
relative_time_pattern = re.compile(ur'(\d+小時|)\d+分前')
absolute_time_pattern = re.compile(ur'\d+年\d+月\d+日 \d+時\d+分')
relative_time_lock = threading.Lock()


class SpiderAM730(common_news_spider.CommonNewsSpider):

    def _get_timestamp_from_relative_time_str(self, t_str):
        with relative_time_lock:
            if relative_time_pattern.findall(t_str):
                hour = 0
                if re.findall(ur'\d+(?=小時)', t_str):
                    hour = int(re.findall(ur'\d+(?=小時)', t_str)[0])
                minute = int(re.findall(ur'\d+(?=分前)', t_str)[0])
                return util.get_now() - hour*3600 - minute*60
            return 0

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = util.get_time_string_from_selectors(doc, {'div.dateforarticle'})
                t_stamp = 0
                if relative_time_pattern.match(t):
                    t_stamp = self._get_timestamp_from_relative_time_str(t)
                elif absolute_time_pattern.match(t):
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
                t = util.get_time_string_from_selectors(doc, {'div.dateforarticle'})
                t_stamp = 0
                if relative_time_pattern.match(t):
                    t_stamp = self._get_timestamp_from_relative_time_str(t)
                elif absolute_time_pattern.match(t):
                    t_stamp = util.get_timestamp_from_string(t)
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h2'})
        t = util.get_time_string_from_selectors(doc, {'div.dateforarticle'})
        t_stamp = 0
        if relative_time_pattern.match(t):
            t_stamp = self._get_timestamp_from_relative_time_str(t)
        elif absolute_time_pattern.match(t):
            t_stamp = util.get_timestamp_from_string(t) + int(time.localtime().tm_sec)
        category = '新聞'
        author = ''
        content = util.get_paragraphs_from_selector(doc, '#mymain')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'AM730'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        am730_seed = {'http://www.am730.com.hk/fresh/'}
        r = requests.get('http://www.am730.com.hk/fresh/')
        d = pq(r.text)
        for op in d('#listnews option').items():
            if op.attr('value'):
                am730_seed.add(op.attr('value'))
        am730_reg = {ur'http://www\.am730\.com\.hk/.*/article/.*'}
        spider_am730 = SpiderAM730('SpiderAM730', am730_seed, am730_reg, THREAD_NUM=5, MAX_DEPTH=0)
        spider_am730.BATCH_NUMBER = util.get_day_stamp() + 10200
        spider_am730.OFFSET = offset
        return spider_am730


if __name__ == '__main__':

    SpiderAM730.PUT_IN_STORAGE = False
    SpiderAM730.start_crawling()
