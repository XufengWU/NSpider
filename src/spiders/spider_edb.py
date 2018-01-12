# -*- coding:utf-8 -*-
import common_news_spider
import util
import threading
import time


class SpiderEDB(common_news_spider.CommonNewsSpider):

    time_cat_dict = {}
    time_cat_dict_lock = threading.RLock()

    def get_filtered_urls(self, task, response):
        response.encoding = 'utf-8'
        doc = self.get_doc(response)
        urls = set()
        for link in self.get_links(doc):
            if link.parent().hasClass('item2'):
                u = self.get_url_of_link(link, doc, task.url)
                u = util.url_para_filter(u, self.AUTO_FILTER_URL_PARAS)
                with self.time_cat_dict_lock:
                    self.time_cat_dict[u] = [link.parent().siblings('.date').text(), link.parent().siblings('.item3').text()]
                    if u and self.task_filter(doc, u, task.url):
                        urls.add(u)
        return urls

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                with self.time_cat_dict_lock:
                    if url in self.time_cat_dict:
                        t = self.time_cat_dict[url][0]
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
                with self.time_cat_dict_lock:
                    if url in self.time_cat_dict:
                        t = self.time_cat_dict[url][0]
                        t_stamp = util.get_timestamp_from_string(t)
                        if t_stamp >= util.get_day_stamp(self.OFFSET):
                            return True
                        return False
                    return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = doc('h1').text()
        t = ''
        category = ''
        with self.time_cat_dict_lock:
            if task.url in self.time_cat_dict:
                t = self.time_cat_dict[task.url][0]
                category = self.time_cat_dict[task.url][1]
        t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_hour*3600 + time.localtime().tm_min*60 + time.localtime().tm_sec
        author = ''
        content = util.get_paragraphs_from_selector(doc, '#content p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'HKEDB'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        edb_seed = {'http://www.edb.gov.hk/tc/news/all.html'}
        spider_edb = SpiderEDB('SpiderEDB',
                               edb_seed,
                               {ur'http://www\.edb\.gov\.hk/.+\.htm.*'},
                               THREAD_NUM=5)
        spider_edb.OFFSET = offset
        spider_edb.BATCH_NUMBER = util.get_day_stamp() + 10470
        return spider_edb


if __name__ == '__main__':
    SpiderEDB.PUT_IN_STORAGE = False
    SpiderEDB.start_crawling()
