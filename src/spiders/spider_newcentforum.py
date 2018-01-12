# -*- coding:utf-8 -*-
import common_news_spider
import util
import threading
import time
import re

news_prefix = 'http://www.ncforum.org.hk'
incomplete_pattern = re.compile(r'/news/.+')


class SpiderNewCenturyForum(common_news_spider.CommonNewsSpider):

    url_time_dict = {}
    url_time_dict_lock = threading.RLock()

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if incomplete_pattern.match(u):
                u = news_prefix + u
        else:
            u = ''
        return u

    def get_filtered_urls(self, task, response):
        doc = self.get_doc(response)
        urls = set()
        for link in self.get_links(doc):
            u = self.get_url_of_link(link, doc, task.url)
            u = util.url_para_filter(u, self.AUTO_FILTER_URL_PARAS)
            with self.url_time_dict_lock:
                self.url_time_dict[u] = link.siblings('span').text()
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

        title = util.get_filtered_title(doc, {'.article-title'})
        t = ''
        with self.url_time_dict_lock:
            t = self.url_time_dict[task.url]
        print t
        t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_hour*3600 + time.localtime().tm_min*60 + time.localtime().tm_sec
        category = '新聞發佈'
        author = ''
        content = util.get_paragraphs_from_selector(doc, '.article-content')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'NewCenturyForum'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        newcent_seed = {'http://www.ncforum.org.hk/news'}
        spider_newcent = SpiderNewCenturyForum('SpiderNewCenturyForum',
                                               newcent_seed,
                                               {ur'http://www\.ncforum\.org\.hk/news/.+'},
                                               THREAD_NUM=5)
        spider_newcent.OFFSET = offset
        spider_newcent.BATCH_NUMBER = util.get_day_stamp() + 10450
        return spider_newcent


if __name__ == '__main__':
    SpiderNewCenturyForum.PUT_IN_STORAGE = False
    SpiderNewCenturyForum.start_crawling()
