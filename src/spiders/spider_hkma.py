# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time

complete_pattern = re.compile(r'http://www\.hkma\.gov\.hk/.+')
news_prefix = 'http://www.hkma.gov.hk'
href_pattern = re.compile(r'(?<=href=").+?(?=")')
title_pattern = re.compile(r'(?<=<title>).+?(?=</title>)')


class SpiderHKMA(common_news_spider.CommonNewsSpider):

    def get_filtered_urls(self, task, response):
        urls = set()
        href_list = re.findall(href_pattern, response.text)
        for href in href_list:
            if not complete_pattern.match(href):
                href = news_prefix + href
            for reg_pattern in self.reg_patterns:
                if reg_pattern.match(href):
                    urls.add(href)
        return urls

    def normal_item_solver(self, item, task, response):

        response.encoding = 'utf-8'
        doc = self.get_doc(response)

        title = re.sub(u'香港金融管理局 - ', '', re.findall(title_pattern, response.text)[0])
        t = re.sub(u'修訂日期: ', '', doc('#lastUpdate').text())
        t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_hour*3600 + time.localtime().tm_min*60 + time.localtime().tm_sec
        category = doc('#content').text().split(' ')[0]
        author = ''
        content = doc('.item').text()

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'HKMA'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        hkma_seed = {'http://www.hkma.gov.hk/chi/key-information/press-releases/' + str(time.localtime().tm_year) + '.shtml',
                     'http://www.hkma.gov.hk/chi/key-information/speeches/' + str(time.localtime().tm_year)}
        day_str = util.get_day_string(offset=offset)
        spider_hkma = SpiderHKMA('SpiderHKMA',
                                 hkma_seed,
                                 {ur'http://www\.hkma\.gov\.hk/chi/.+' + day_str + '.+'},
                                 THREAD_NUM=5)
        spider_hkma.OFFSET = offset
        spider_hkma.BATCH_NUMBER = util.get_day_stamp() + 10480
        return spider_hkma


if __name__ == '__main__':
    SpiderHKMA.PUT_IN_STORAGE = False
    SpiderHKMA.start_crawling()
