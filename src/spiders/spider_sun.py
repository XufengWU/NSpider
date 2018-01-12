# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import requests
from pyquery import PyQuery as pq


prefix = u'http://the-sun.on.cc'
complete_pattern = re.compile(ur'(http|https)://.+')
today_date_pattern = re.compile(util.get_day_string())
cat_pattern = re.compile(ur'(?<=cnt/).+?(?=/)')
charset_pattern = re.compile(ur'(?<=charset=).+')


class SpiderSun(common_news_spider.CommonNewsSpider):

    def send_request(self, task):
        task.fetched_at = util.get_now()
        r = requests.get(task.url, timeout=self.RESPONSE_TIMEOUT_VALUE)
        d = pq(r.text)
        if d('meta'):
            for meta in d('meta').items():
                if charset_pattern.findall(meta.attr('content')):
                    r.encoding = charset_pattern.findall(meta.attr('content'))[0]
                    if r.encoding == 'big5':
                        r.encoding = 'big5hkscs'
                    return r
        r.encoding = 'big5hkscs'
        return r

    def get_url_of_link(self, link, doc, doc_url):
        u = ''
        if link.attr('href'):
            u = link.attr('href')
        if u is not '' and not complete_pattern.match(u):
            u = prefix + u
        return u

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1', 'font.heading', 'font[size="+2"]'})
        t = util.get_day_string(offset=self.OFFSET)
        t_stamp = util.get_day_stamp(self.OFFSET)
        category = ''
        if cat_pattern.findall(task.url):
            cat_word = cat_pattern.findall(task.url)[0]
            category = doc('.' + cat_word).text()
        if category == '':
            category = re.sub(ur' .*', u'', doc('td font').text())
        author = ''
        content = util.get_paragraphs_from_selector(doc, '.newsText p')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, '#contentAD1 p')
        if content == '':
            _doc = doc('#contentAD1')
            _doc.remove('table')
            _doc.remove('span')
            content = util.get_paragraphs_from_selector(_doc, 'div')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, 'dd')
        if content == '':
            content = doc('.caption').next_all('p').text()
        if content == '':
            _doc = doc.parent('.caption').parent()
            _doc.remove('table').remove('span')
            content = _doc.text()
        if content == '':
            _doc = doc('.caption').parent()
            content = _doc.remove('table').text()
        if content == '':
            content = doc('.summaryPara').text()

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'SunDaily'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        sun_seed = {'http://the-sun.on.cc/cnt/sitemap/' +
                    util.get_day_string(offset=offset) +
                    '/index.html', 'http://orientaldaily.on.cc/'}
        sun_reg = {ur'http://the-sun\.on\.cc/.+' +
                   r'(?<!fea/)' +
                   util.get_day_string(offset=offset) +
                   r'(?!/index)' +
                   r'/[\d\w_]+.html'}
        spider_sun = SpiderSun('SpiderSun', sun_seed, sun_reg, THREAD_NUM=15)
        spider_sun.OFFSET = offset
        spider_sun.BATCH_NUMBER = util.get_day_stamp() + 10320
        return spider_sun


if __name__ == '__main__':

    SpiderSun.PUT_IN_STORAGE = False
    SpiderSun.start_crawling()
