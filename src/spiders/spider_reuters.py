# -*- coding:utf-8 -*-
import common_news_spider
import util
import re


complete_pattern = re.compile(ur'http://.+')
prefix = 'http://cn.reuters.com'


class SpiderReuters(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = prefix + u
        else:
            u = ''
        return u

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = doc('meta[property="og:article:published_time"]').attr('content')
                t_stamp = util.get_timestamp_from_string(t) + 8 * 3600
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if not reg_pattern.match(doc_url):
                    return True
                t = doc('meta[property="og:article:published_time"]').attr('content')
                t_stamp = util.get_timestamp_from_string(t) + 8 * 3600
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1'})
        t = doc('meta[property="og:article:published_time"]').attr('content')
        t_stamp = util.get_timestamp_from_string(t) + 8 * 3600
        category = doc('.article-section').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, '#article-text p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'Reuters CN'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        reuters_seed = {'http://cn.reuters.com/markets/hongkong'}
        spider_reuters = SpiderReuters('SpiderReuters',
                                       reuters_seed,
                                       {ur'http://cn\.reuters\.com/article/.+'},
                                       THREAD_NUM=10)
        spider_reuters.BATCH_NUMBER = util.get_day_stamp() + 10560
        spider_reuters.OFFSET = offset
        return spider_reuters


if __name__ == '__main__':

    SpiderReuters.PUT_IN_STORAGE = True
    SpiderReuters.start_crawling()
