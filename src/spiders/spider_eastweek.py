# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time


prefix = u'http://eastweek.my-magazine.me'
complete_pattern = re.compile(ur'http://.+')
date_pattern = re.compile(ur'\d{4} 年 \d{2} 月 \d{2} 日')


class SpiderEastWeek(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = ''
        if link.attr('href'):
            u = link.attr('href')
            if not complete_pattern.match(u):
                u = prefix + u
        return u

    def page_filter(self, doc, url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if date_pattern.findall(doc('span.pull-right').text()):
                    t = util.get_time_string_from_selectors(doc, {'span.pull-right'}, date_patterns={date_pattern})
                    t_stamp = util.get_timestamp_from_string(t, time_format=u'%Y 年 %m 月 %d 日')
                    if t_stamp >= util.get_day_stamp(self.OFFSET):
                        return True
        return wanted

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if date_pattern.findall(doc('span.pull-right').text()):
                    t = util.get_time_string_from_selectors(doc, {'span.pull-right'}, date_patterns={date_pattern})
                    t_stamp = util.get_timestamp_from_string(t, time_format=u'%Y 年 %m 月 %d 日')
                    if t_stamp >= util.get_day_stamp(self.OFFSET):
                        return True
                    return False
                return True
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        item.raw = doc.text()
        item.title = util.get_filtered_title(doc, {'title'}, u'東周網【東周刊官方網站】| - .+')
        item.t = util.get_time_string_from_selectors(doc, {'span.pull-right'}, date_patterns={date_pattern})
        item.t_stamp = util.get_timestamp_from_string(item.t, time_format=u'%Y 年 %m 月 %d 日') + time.localtime().tm_hour*3600 + time.localtime().tm_min*60 + time.localtime().tm_sec
        item.fetched_at = task.fetched_at
        item.category = re.sub(ur'.*\s+', u'', doc('.default-group a').text())
        item.author = ''
        item.content = util.get_paragraphs_from_selector(doc, 'div.view-content p')
        item.url = task.url
        item.source = 'EastWeek'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        eastweek_seed = {'http://eastweek.my-magazine.me/main/'}
        eastweek_reg = {ur'http://eastweek\.my-magazine\.me/main/\d+'}
        spider_eastweek = SpiderEastWeek('SpiderEastWeek', eastweek_seed, eastweek_reg, THREAD_NUM=10)
        spider_eastweek.BATCH_NUMBER = util.get_day_stamp() + 10240
        spider_eastweek.OFFSET = offset
        return spider_eastweek


if __name__ == '__main__':

    SpiderEastWeek.PUT_IN_STORAGE = False
    SpiderEastWeek.start_crawling()
