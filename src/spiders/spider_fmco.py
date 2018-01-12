# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import requests
import time

complete_pattern = re.compile(ur'http://.+')
incomplete_pattern = re.compile(ur'\./t\d+\.htm')
date_pattern = re.compile(r'\d{4}/\d\d/\d\d')
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2832.2 Safari/537.36'}


class SpiderFmco(common_news_spider.CommonNewsSpider):

    def send_request(self, task):
        r = requests.get(task.url, headers=headers, timeout=self.RESPONSE_TIMEOUT_VALUE)
        task.fetched_at = util.get_now()
        return r

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if incomplete_pattern.match(u):
                u = re.sub(r't\d+.+', '', doc_url) + u[2:]
        else:
            u = ''
        return u

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = ''
                if doc('#News_Body_Time'):
                    t = date_pattern.findall(str(doc('#News_Body_Time')))[0]
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
                t = ''
                if doc('#News_Body_Time'):
                    t = date_pattern.findall(str(doc('#News_Body_Time')))[0]
                t_stamp = util.get_timestamp_from_string(t)
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = doc('#News_Body_Title').text()
        t = ''
        if doc('#News_Body_Time'):
            t = date_pattern.findall(str(doc('#News_Body_Time')))[0]
        t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_hour*3600 + time.localtime().tm_min*60 + time.localtime().tm_sec
        category = doc('.Top_Index_A a:last-child').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, '#News_Body_Txt_A p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'FMCOPRC'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        fmco_seed = {'http://www.fmcoprc.gov.hk/chn/gsxw/',
                     'http://www.fmcoprc.gov.hk/chn/zydt/',
                     'http://www.fmcoprc.gov.hk/chn/qwsy/',
                     'http://www.fmcoprc.gov.hk/chn/gsfc/'}
        spider_fmco = SpiderFmco('SpiderFmco',
                                 fmco_seed,
                                 {u'http://www\.fmcoprc\.gov\.hk/chn/.+t.+\.htm'},
                                 THREAD_NUM=5)
        spider_fmco.OFFSET = offset
        spider_fmco.BATCH_NUMBER = util.get_day_stamp() + 10420
        return spider_fmco


if __name__ == '__main__':
    SpiderFmco.PUT_IN_STORAGE = False
    SpiderFmco.start_crawling()
