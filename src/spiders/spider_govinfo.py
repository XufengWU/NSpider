# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time
import threading


complete_pattern = re.compile(ur'(http|https)://.+')
half_complete_pattern = re.compile(ur'/gia/general/.+')
half_prefix = 'http://www.info.gov.hk'
charset_pattern = re.compile(r'(?<=charset=).+?(?=")')


class SpiderGovInfoNews(common_news_spider.CommonNewsSpider):

    charset = ''
    charset_lock = threading.RLock()

    def find_charset(self, res):
        char_string = res.text
        if charset_pattern.findall(char_string):
            charset = charset_pattern.findall(char_string)[0]
            return charset
        return 'big5'

    def get_url_of_link(self, link, doc, doc_url):
        prefix = 'http://www.info.gov.hk/gia/general/' + util.get_day_string(offset=self.OFFSET)[:-2] + '/'
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                if half_complete_pattern.match(u):
                    u = half_prefix + u
                else:
                    u = prefix + u
        else:
            u = ''
        return u

    def normal_item_solver(self, item, task, response):

        with self.charset_lock:
            if self.charset == '':
                self.charset = self.find_charset(response)
        response.encoding = self.charset
        doc = self.get_doc(response)

        if doc:
            title = doc('title').text()
            if title == '':
                if re.findall(r'(?<=<title>).+(?=</title>)', response.text):
                    title = re.findall(r'(?<=<title>).+(?=</title>)', response.text)[0]
            t = util.get_day_string(offset=self.OFFSET)
            t_stamp = util.get_day_stamp(offset=self.OFFSET) + time.localtime().tm_min*60 + time.localtime().tm_sec
            category = ''
            author = ''
            content = util.get_paragraphs_from_selector(doc, '#pressrelease p')
            if content == '':
                content = util.get_paragraphs_from_selector(doc, '#pressrelease')
            if content == '':
                content = util.get_paragraphs_from_selector(doc, 'td p')
            content = re.sub(ur'＊+\n', '', content)

            item.raw = response.text
            item.title = title
            item.t = t
            item.t_stamp = t_stamp
            item.fetched_at = task.fetched_at
            item.category = category
            item.author = author
            item.content = content
            item.url = task.url
            item.source = 'GovInfoNews'
            item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        day_str = util.get_day_string(offset=offset)
        day_str = day_str[:-2] + '/' + day_str[-2:]
        govinfo_seed = {'http://www.info.gov.hk/gia/general/' + day_str + 'c.htm'}
        govinfo_reg = {ur'http://www\.info\.gov\.hk/gia/general/' + day_str + '.+'}
        spider_govinfo = SpiderGovInfoNews('SpiderGovInfoNews', govinfo_seed, govinfo_reg, THREAD_NUM=10)
        spider_govinfo.OFFSET = offset
        spider_govinfo.BATCH_NUMBER = util.get_day_stamp(offset) + 10600
        return spider_govinfo


if __name__ == '__main__':

    SpiderGovInfoNews.PUT_IN_STORAGE = True
    SpiderGovInfoNews.start_crawling()
