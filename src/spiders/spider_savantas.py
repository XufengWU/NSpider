# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time


class SpiderSavantas(common_news_spider.CommonNewsSpider):

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                meta_txt = doc('.metaStuff').text()
                t = re.findall(ur'[^\s]+月.+', meta_txt)[0]
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
                meta_txt = doc('.metaStuff').text()
                t = re.findall(ur'[^\s]+月.+', meta_txt)[0]
                t_stamp = util.get_timestamp_from_string(t)
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = doc('h1').text()
        meta_txt = doc('.metaStuff').text()
        t = re.findall(ur'[^\s]+月.+', meta_txt)[0]
        t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_hour*3600 + time.localtime().tm_min*60 + time.localtime().tm_sec
        category = doc('#crumbs a').text().split(' ')[-1]
        author = meta_txt.split(' ')[0]
        content = util.get_paragraphs_from_selector(doc, '.entry p')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, '.entry div')
        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'Savantas'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        savantas_seed = {'http://www.savantas.org/'}
        util.add_hrefs('http://www.savantas.org/', {'#navigation a'}, savantas_seed)
        spider_savantas = SpiderSavantas('SpiderSavantas',
                                         savantas_seed,
                                         {ur'http://www.savantas.org/\?p=\d+'},
                                         THREAD_NUM=5)
        spider_savantas.OFFSET = offset
        spider_savantas.BATCH_NUMBER = util.get_day_stamp() + 10460
        return spider_savantas

if __name__ == '__main__':
    SpiderSavantas.PUT_IN_STORAGE = False
    SpiderSavantas.start_crawling()
