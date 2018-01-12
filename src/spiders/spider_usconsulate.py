# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time

date_pattern = re.compile(str(time.localtime().tm_year) + r'\d{4}')
news_prefix = 'https://hongkong.usconsulate.gov'
complete_pattern = re.compile(r'https://hongkong\.usconsulate\.gov.+')


class SpiderUSConsulate(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = news_prefix + u
        else:
            u = ''
        return u

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = doc('#middle-content-article h1').text()
        t = date_pattern.findall(task.url)[0]
        t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_hour*3600 + time.localtime().tm_min*60 + time.localtime().tm_sec
        category = doc('#menu-inside .active').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, '#middle-content-article p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'USConsulate'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        usconsulate_seed = {'https://hongkong.usconsulate.gov/',
                            'https://hongkong.usconsulate.gov/pas_pr_' + str(time.localtime().tm_year) + '.html',
                            'https://hongkong.usconsulate.gov/cg_ch_speeches.html',
                            'https://hongkong.usconsulate.gov/events.html'}
        day_str = util.get_day_string(offset=offset)
        spider_usconsulate = SpiderUSConsulate('SpiderUSConsulate',
                                               usconsulate_seed,
                                               {ur'https://hongkong.usconsulate.gov/.+' + day_str + '.+'},
                                               THREAD_NUM=10)
        spider_usconsulate.OFFSET = offset
        spider_usconsulate.BATCH_NUMBER = util.get_day_stamp() + 10500
        return spider_usconsulate


if __name__ == '__main__':
    SpiderUSConsulate.PUT_IN_STORAGE = False
    SpiderUSConsulate.start_crawling()

