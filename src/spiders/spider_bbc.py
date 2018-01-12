# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time

complete_pattern = re.compile(ur'http://.+')
news_prefix = 'http://www.bbc.com'
date_pattern = re.compile(ur'\d\d\d\d年 \d+月 \d+日')


class SpiderBBC(common_news_spider.CommonNewsSpider):

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

        title = util.get_filtered_title(doc, {'title'}, u' - BBC 中文网| BBC Zhongwen')
        t = ''
        t_stamp = 0
        if doc('.story-body .mini-info-list .date').attr('data-datetime'):
            t = doc('.story-body .mini-info-list .date').attr('data-datetime')
            t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_sec
        elif doc('.timeline-status h3') and date_pattern.findall(doc('.timeline-status h3').text()):
            t = date_pattern.findall(doc('.timeline-status h3').text())[0]
            t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_sec
        elif doc('.story-body .date strong') and date_pattern.findall(doc('.story-body .date strong').text()):
            t = date_pattern.findall(doc('.story-body .date strong').text())[0]
            t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_sec
        category = doc('meta[property="article:section"]').attr('content')
        author = doc('span.byline__name').text()
        content = util.get_paragraphs_from_selector(doc, 'div[property="articleBody"] p')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, '.article-wrapper p')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, '.map-body p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'BBC Chinese'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        bbc_seed = set()
        util.add_hrefs('http://www.bbc.com/zhongwen/trad/', {'ul.navigation-wide-list a'}, bbc_seed, news_prefix)
        bbc_seed.add('http://www.bbc.com/zhongwen/trad/hong_kong_review')
        day_str = util.get_day_string(offset=offset)
        day_str = day_str[2:]
        spider_bbc = SpiderBBC('SpiderBBC',
                               bbc_seed,
                               {ur'http://www.bbc.com/.+' + day_str + '.+'},
                               THREAD_NUM=5)
        spider_bbc.OFFSET = offset
        spider_bbc.BATCH_NUMBER = util.get_day_stamp() + 10360
        return spider_bbc


if __name__ == '__main__':
    SpiderBBC.PUT_IN_STORAGE = False
    SpiderBBC.start_crawling()
