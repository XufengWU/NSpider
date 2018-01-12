# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import requests
from pyquery import PyQuery as pq
import time


complete_pattern = re.compile(ur'http://www\.macaodaily\.com/.*')
t_pattern = re.compile(ur'\d{4}(?= *年)')


class SpiderMacao(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        current_day_string = util.get_day_string(offset=self.OFFSET)
        day_string = current_day_string[0:4] + '-' + current_day_string[4:6] + '/' + current_day_string[6:8]
        index_prefix = 'http://www.macaodaily.com/html/' + day_string + '/'
        if u is not None:
            if not complete_pattern.match(u):
                u = index_prefix + u
        else:
            u = ''
        return u

    def send_request(self, task):
        r = requests.get(task.url, timeout=self.RESPONSE_TIMEOUT_VALUE)
        r.encoding = 'utf8'
        task.fetched_at = util.get_now()
        return r

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = doc('table[id=table15] strong').text()
        t = doc('table[id=table23]').text()
        year = re.findall(t_pattern, t)[0]
        mon = int(re.findall(ur'\d{1,2}(?= *月)', t)[0])
        day = int(re.findall(ur'\d{1,2}(?= *日)', t)[0])
        t_stamp = int(time.mktime(time.strptime(year + ('%02d' % mon) + ('%02d' % day), '%Y%m%d')))
        current_date = str(time.localtime().tm_year) + ('%02d' % time.localtime().tm_mon) + (
            '%02d' % time.localtime().tm_mday)
        if t_stamp >= int(time.mktime(time.strptime(current_date, "%Y%m%d"))):
            t_stamp = int(time.time())
        category = doc('table[id=table22] strong').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, 'founder-content p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'Macao'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        current_day_string = util.get_day_string(offset=offset)
        day_string = current_day_string[0:4] + '-' + current_day_string[4:6] + '/' + current_day_string[6:8]
        index_prefix = 'http://www.macaodaily.com/html/' + day_string + '/'
        macao_seed = {index_prefix + 'node_2.htm'}
        _index = requests.get(index_prefix + 'node_2.htm')
        d = pq(_index.text)
        for a in d('table.unnamed1 a').items():
            if a.attr('href') is not None:
                macao_seed.add(index_prefix + a.attr('href'))
        spider_macao = SpiderMacao('SpiderMacao', macao_seed,
                                   {ur'http://www\.macaodaily\.com/html/' + day_string + ur'/content_.*'},
                                   THREAD_NUM=10)
        spider_macao.BATCH_NUMBER = util.get_day_stamp() + 10080
        spider_macao.OFFSET = offset
        return spider_macao


if __name__ == '__main__':

    SpiderMacao.PUT_IN_STORAGE = False
    SpiderMacao.start_crawling()
