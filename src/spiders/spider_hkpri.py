# -*- coding:utf-8 -*-
import common_news_spider
import util
import threading
import time
import re

news_prefix = 'http://www.news.cn/gangao/'
cat_pattern = re.compile('(?<=\.hk/)\w+')


class SpiderHKPRI(common_news_spider.CommonNewsSpider):

    url_time_dict = {}
    url_time_dict_lock = threading.RLock()

    def get_filtered_urls(self, task, response):
        doc = self.get_doc(response)
        urls = set()
        for link in self.get_links(doc):
            u = self.get_url_of_link(link, doc, task.url)
            u = util.url_para_filter(u, self.AUTO_FILTER_URL_PARAS)
            with self.url_time_dict_lock:
                self.url_time_dict[u] = link.parent().siblings('.entry-meta').children('.entry-date').text()
                if u and self.task_filter(doc, u, task.url):
                    urls.add(u)
        return urls

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                with self.url_time_dict_lock:
                    if url in self.url_time_dict:
                        t = self.url_time_dict[url]
                        t_stamp = util.get_timestamp_from_string(t)
                        if t_stamp >= util.get_day_stamp(self.OFFSET):
                            return True
                        return False
                    return False
        return False

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if not reg_pattern.match(doc_url):
                    return True
                with self.url_time_dict_lock:
                    if url in self.url_time_dict:
                        t = self.url_time_dict[url]
                        t_stamp = util.get_timestamp_from_string(t)
                        if t_stamp >= util.get_day_stamp(self.OFFSET):
                            return True
                        return False
                    return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'head title'}, u' | Hong Kong Policy Research Institute')
        t = ''
        with self.url_time_dict_lock:
            t = self.url_time_dict[task.url]
        t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_hour*3600 + time.localtime().tm_min*60 + time.localtime().tm_sec
        category = ''
        if cat_pattern.findall(task.url):
            category = cat_pattern.findall(task.url)[0]
        author = ''
        content = util.get_paragraphs_from_selector(doc, '.entry-item p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'HKPRI'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        hkpri_seed = {'http://www.hkpri.org.hk/event/',
                      'http://www.hkpri.org.hk/researchreport/',
                      'http://www.hkpri.org.hk/category/%E5%B0%88%E9%A1%8C%E8%A9%95%E8%AB%96/',
                      'http://www.hkpri.org.hk/category/%E9%A6%99%E6%B8%AF%E9%A1%98%E6%99%AF%E5%B0%8D%E8%AB%87/'}
        spider_hkpri = SpiderHKPRI('SpiderHKPRI',
                                   hkpri_seed,
                                   {ur'http://www.hkpri.org.hk/(event|researchreport|category|commentary)/.+'},
                                   THREAD_NUM=5)
        spider_hkpri.OFFSET = offset
        spider_hkpri.BATCH_NUMBER = util.get_day_stamp() + 10440
        return spider_hkpri


if __name__ == '__main__':
    SpiderHKPRI.PUT_IN_STORAGE = False
    SpiderHKPRI.start_crawling()
