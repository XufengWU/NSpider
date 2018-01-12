# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time


complete_pattern = re.compile(ur'http://.+')
date_pattern = re.compile(ur'\d{4}-\d\d-\d\d')
cat_pattern_in_url = re.compile(ur'(?<=home/).+?(?=/)')
prefix = 'http://news.tvb.com'


class SpiderTVB(common_news_spider.CommonNewsSpider):

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
                t = util.get_time_string_from_selectors(doc, {'span.time'})
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
                t = util.get_time_string_from_selectors(doc, {'span.time'})
                t_stamp = util.get_timestamp_from_string(t)
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        t = util.get_time_string_from_selectors(doc, {'span.time'})
        t_stamp = util.get_timestamp_from_string(t) + int(time.localtime().tm_sec)
        title = doc('h4').remove('span').text()
        category = doc('#topMenu a.on').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, '#c1_afterplayer pre')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'TVB'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        tvb_seed = {'http://news.tvb.com/'}
        util.add_hrefs(url='http://news.tvb.com/',
                       selectors={'#topMenu a'},
                       seeds=tvb_seed,
                       seed_patterns={re.compile(r'http://news\.tvb\.com/list/\d+/')})
        spider_tvb = SpiderTVB('SpiderTVB',
                               tvb_seed,
                               {ur'http://news\.tvb\.com/\w+/[\d\w]{10,}'},
                               THREAD_NUM=10, MAX_DEPTH=2)
        spider_tvb.BATCH_NUMBER = util.get_day_stamp() + 10290
        spider_tvb.OFFSET = offset
        return spider_tvb


if __name__ == '__main__':

    SpiderTVB.PUT_IN_STORAGE = False
    SpiderTVB.start_crawling(offset=1)
