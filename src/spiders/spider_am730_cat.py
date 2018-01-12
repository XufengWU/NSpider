# -*- coding:utf-8 -*-
import common_news_spider
import util
import requests
from pyquery import PyQuery as pq


class SpiderAM730Categories(common_news_spider.CommonNewsSpider):

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = util.get_time_string_from_selectors(doc, {'#article_date'})
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
                t = util.get_time_string_from_selectors(doc, {'#article_date'})
                t_stamp = util.get_timestamp_from_string(t)
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h2'})
        t = util.get_time_string_from_selectors(doc, {'#article_date'})
        t_stamp = util.get_now()
        category = doc('#article_date +div a:last-child').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, '.wordsnap div')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, '.wordsnap')

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
        am730_cat_seed = {'http://www.am730.com.hk/home'}
        r = requests.get('http://www.am730.com.hk/home')
        d = pq(r.text)
        for op in d('#listnews option').items():
            if op.attr('value'):
                am730_cat_seed.add('http://www.am730.com.hk/' + op.attr('value'))
        am730_cat_reg = {ur'http://www\.am730\.com\.hk/article-.*'}
        spider_am730_cat = SpiderAM730Categories('SpiderAM730Categories', am730_cat_seed, am730_cat_reg, THREAD_NUM=5, MAX_DEPTH=2)
        spider_am730_cat.BATCH_NUMBER = util.get_day_stamp() + 10201
        spider_am730_cat.OFFSET = offset
        return spider_am730_cat


if __name__ == '__main__':

    SpiderAM730Categories.PUT_IN_STORAGE = False
    SpiderAM730Categories.start_crawling()
