# -*- coding:utf-8 -*-
import common_news_spider
import util
import re


complete_pattern = re.compile(ur'http://.+')
news_prefix = 'http://news.hkpeanut.com/'


class SpiderPeanut(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = news_prefix + u
        else:
            u = ''
        return u

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = doc('meta[property="article:published_time"]').attr('content')
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
                t = doc('meta[property="article:published_time"]').attr('content')
                t_stamp = util.get_timestamp_from_string(t)
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = doc('meta[property="og:title"]').attr('content')
        t = doc('meta[property="article:published_time"]').attr('content')
        t_stamp = util.get_timestamp_from_string(t)
        category = doc('meta[property="article:section"]').attr('content')
        author = ''
        content = util.get_paragraphs_from_selector(doc, '.entry-content p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'Peanut'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        peanut_seed = {'http://www.hkpeanut.com', u'http://news.hkpeanut.com/archives/category/%E8%A6%81%E8%81%9E%E6%B8%AF%E8%81%9E'}
        spider_peanut = SpiderPeanut('SpiderPeanut',
                                     peanut_seed,
                                     {ur'http://news.hkpeanut.com/archives/\d+'},
                                     THREAD_NUM=5)
        spider_peanut.OFFSET = offset
        spider_peanut.BATCH_NUMBER = util.get_day_stamp() + 10340
        return spider_peanut


if __name__ == '__main__':
    SpiderPeanut.PUT_IN_STORAGE = False
    SpiderPeanut.start_crawling()
