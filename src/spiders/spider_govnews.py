# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import common_news_spider
import util
import re
from pyquery import PyQuery as pq
import requests
import time


tc_time_pattern = re.compile(ur'/tc/.*/\d\d\d\d/\d\d/.*')
date_pattern = re.compile(ur'(?<=\d\d\d\d/\d\d/)\d{8}')
cat_pattern = re.compile(ur'/tc/.*(?=/html.*)')


class SpiderGov(common_news_spider.CommonNewsSpider):

    def send_request(self, task):
        r = requests.get(task.url, timeout=self.RESPONSE_TIMEOUT_VALUE)
        r.encoding = 'utf-8'
        task.fetched_at = util.get_now()
        return r

    def get_url_of_link(self, link, doc, doc_url):
        u = str(link.attr('href'))
        if tc_time_pattern.match(u):
            u = 'http://www.news.gov.hk' + u
        return u

    def page_filter(self, doc, url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                soup = BeautifulSoup(str(doc), 'lxml')
                if soup.select('meta[name=last-modified]').__len__() > 0:
                    tm_day = time.localtime().tm_mday
                    search_offset = self.OFFSET
                    if tm_day > search_offset:
                        tm_day -= search_offset
                    else:
                        tm_day = 1
                    current_date = str(time.localtime().tm_year) + ('%02d' % time.localtime().tm_mon) + ('%02d' % tm_day)
                    # the timestamp of current date
                    t_stamp = int(time.mktime(time.strptime(current_date, '%Y%m%d')))
                    if int(time.mktime(time.strptime(soup.select('meta[name=last-modified]')[0]['content'],
                                                     "%d/%m/%Y %I:%M:%S %p"))) >= t_stamp:
                        wanted = True
        return wanted

    def task_filter(self, doc, url, doc_url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                post_date = date_pattern.findall(url)[0]
                tm_day = time.localtime().tm_mday
                search_offset = self.OFFSET
                if tm_day > search_offset:
                    tm_day -= search_offset
                else:
                    tm_day = 1
                current_date = str(time.localtime().tm_year) + ('%02d' % time.localtime().tm_mon) + ('%02d' % tm_day)
                # the timestamp of current date
                t_stamp = int(time.mktime(time.strptime(current_date, '%Y%m%d')))
                if int(time.mktime(time.strptime(post_date, "%Y%m%d"))) >= t_stamp:
                    wanted = True
        return wanted

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)
        soup = BeautifulSoup(str(doc), 'lxml')

        item.raw = doc.text()
        item.title = re.sub(u'.* - ', u'', soup.title.string)
        item.t = soup.select('meta[name=last-modified]')[0]['content']
        item.t_stamp = util.get_timestamp_from_string(item.t, time_format='%d/%m/%Y %I:%M:%S %p')
        item.fetched_at = task.fetched_at
        cat_href = cat_pattern.findall(task.url)[0] + '/index.shtml'
        item.category = soup.select('a[href='+cat_href+']')[0].string
        item.author = ''
        content_list = soup.select('div[id=newsContent] p')
        content = ''
        for p in content_list:
            if p.string is not None:
                content = content + p.string + u'\n'
        if content == '':
            content_list = soup.select('#content1 p')
            for p in content_list:
                if p.string is not None:
                    content = content + p.string + u'\n'
        item.content = content
        item.url = task.url
        item.source = 'GovNews'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.imgItem img').items():
            if img.attr('src') != '':
                media_u = img.attr('src')
                media_u = 'http://www.news.gov.hk' + media_u
                des = ''
                if img.attr('alt'):
                    des = img.attr('alt')
                media = self.NewsItem.MediaItem(media_url=media_u, type='image', description=des,
                                                created_at=item.fetched_at)
                item.media_list.append(media)
        for a in doc('iframe').items():
            if a.attr('src') and re.match(r'.*youtube\.com.+', a.attr('src')):
                media_u = a.attr('src')
                media = self.NewsItem.MediaItem(media_url=media_u, type='youtube', description='',
                                                created_at=item.fetched_at)
                item.media_list.append(media)

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        gov_seed = set()
        gov_seed.add('http://www.news.gov.hk/tc/index.shtml')
        gov_r = requests.get('http://www.news.gov.hk/tc/index.shtml')
        gov_index = pq(gov_r.text)
        gov_seed.add('http://archive.news.gov.hk/tc/city_life/html/' + str(time.localtime().tm_year) + '/' + (
        '%02d' % time.localtime().tm_mon) + '/index.shtml')
        gov_seed.add('http://archive.news.gov.hk/tc/record/html/' + str(time.localtime().tm_year) + '/' + (
        '%02d' % time.localtime().tm_mon) + '/index.shtml')
        gov_sub_cats = gov_index('div[id=subnav] a').items()
        for a in gov_sub_cats:
            url_a = a.attr('href')
            url_a = 'http://archive.news.gov.hk' + url_a[:-11] + 'html/' + str(time.localtime().tm_year) + '/' + (
            '%02d' % time.localtime().tm_mon) + '/index.shtml'
            gov_seed.add(url_a)
        spider_gov = SpiderGov('SpiderGov', gov_seed, {ur'http://.*\.news\.gov\.hk/tc/.*/\d\d\d\d/\d\d/\d+_\d+.*'},
                               THREAD_NUM=10, MAX_DEPTH=2)
        spider_gov.AUTO_FILTER_URL_PARAS = True
        spider_gov.OFFSET = offset
        spider_gov.BATCH_NUMBER = util.get_day_stamp() + 10004
        return spider_gov


if __name__ == '__main__':

    SpiderGov.PUT_IN_STORAGE = False
    SpiderGov.start_crawling(offset=1)
