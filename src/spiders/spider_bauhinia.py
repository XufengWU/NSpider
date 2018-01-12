# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time

date_pattern = re.compile(r'\d{4}-\d\d-\d\d')


class SpiderBauhinia(common_news_spider.CommonNewsSpider):

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = util.get_time_string_from_selectors(doc, {'h5 small'}, {date_pattern})
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
                t = util.get_time_string_from_selectors(doc, {'h5 small'}, {date_pattern})
                t_stamp = util.get_timestamp_from_string(t)
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def normal_item_solver(self, item, task, response):

        response.encoding = 'utf-8'
        doc = self.get_doc(response)

        title = doc('#page-h1').text()
        t = util.get_time_string_from_selectors(doc, {'h5 small'}, {date_pattern})
        t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_hour*3600 + time.localtime().tm_min*60 + time.localtime().tm_sec
        category = doc('h5 small a').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, '.content-show p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'Bauhinia'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        bauhinia_seed = {'http://www.bauhinia.org/index.php/zh-CN/search/all/any/cat-any/' + str(time.localtime().tm_year)}
        spider_bauhinia = SpiderBauhinia('SpiderBauhinia',
                                         bauhinia_seed,
                                         {ur'http://www\.bauhinia\.org/index\.php/zh-CN/\w+/\d+'},
                                         THREAD_NUM=10)
        spider_bauhinia.OFFSET = offset
        spider_bauhinia.BATCH_NUMBER = util.get_day_stamp() + 10490
        return spider_bauhinia


if __name__ == '__main__':
    SpiderBauhinia.PUT_IN_STORAGE = False
    SpiderBauhinia.start_crawling()

