# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import copy
import re
from pyquery import PyQuery as pq


news_prefix = u'http://www.881903.com/Page/ZH-TW/'
cat_prefix = u'http://www.881903.com'
cat_page_pattern = re.compile(ur'http://www\.881903\.com/Page/ZH-TW/news\.aspx\?csid=[_\d]+')
complete_pattern = re.compile(ur'http://.+detail.+')
total_page_pattern = re.compile(ur'(?<=/)\d+(?=頁)')
incomplete_pattern = re.compile(ur'.+detail.+')


class SpiderCommercialRadio(common_news_spider.CommonNewsSpider):

    CRAWL_NEXT = True

    def get_url_of_link(self, link, doc, doc_url):
        u = ''
        if link.attr('href'):
            u = link.attr('href')
            if not complete_pattern.match(u):
                if incomplete_pattern.match(u):
                    u = news_prefix + u
                else:
                    u = ''
            if re.findall(ur'ItemId=', u):
                u = re.sub(ur'&csid=.+', u'', u)
        return u

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = util.get_time_string_from_selectors(doc, {'#divnewsTextDate', '#part6808_ctl00_lblDetailDate'})
                t_stamp = util.get_timestamp_from_string(t, '%d.%m.%Y %H:%M')
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def task_filter(self, doc, url, doc_url):
        if not self.CRAWL_NEXT:
            return False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if not reg_pattern.match(doc_url):
                    return True
                t = util.get_time_string_from_selectors(doc, {'#divnewsTextDate', '#part6808_ctl00_lblDetailDate'})
                t_stamp = util.get_timestamp_from_string(t, '%d.%m.%Y %H:%M')
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, u'881903.com 商業電台 - ')
        t = util.get_time_string_from_selectors(doc, {'#divnewsTextDate', '#part6808_ctl00_lblDetailDate'})
        t_stamp = util.get_timestamp_from_string(t, '%d.%m.%Y %H:%M') + int(time.localtime().tm_sec)
        category = doc('#part8425_ctl00_divtitle').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, '#divnewsTextContent p')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, '#tdContent p')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, '.newsTextContent2')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'CommercialRadio'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=1):
        day_str = util.get_day_string('.', 'inverse', offset=offset)
        commercial_seed = {'http://www.881903.com/Page/ZH-TW/news.aspx?sdate='+day_str+'&csid=261_341'}
        util.add_hrefs(url='http://www.881903.com/Page/ZH-TW/news.aspx?'+day_str+'&csid=261_341', seeds=commercial_seed,
                       selectors={'#newsCategoryTab a'}, prefix=cat_prefix)
        _seed = copy.deepcopy(commercial_seed)
        for seed in _seed:
            if cat_page_pattern.match(seed):
                r = util.get_safe_response(seed)
                if r:
                    d = pq(r.text)
                    if re.findall(total_page_pattern, d('.Font_Article_CH').text()):
                        total_page = int(re.findall(total_page_pattern, d('.Font_Article_CH').text())[0])
                        for i in range(total_page):
                            commercial_seed.add(seed + '&page=' + str(i+1))
        ''''
        r = requests.get('http://www.881903.com/Page/ZH-TW/index.aspx')
        d = pq(r.text)
        for a in d('.header2012 ul li a').items():
            if a.attr('href'):
                u = a.attr('href')
                if not complete_pattern.match(u):
                    if incomplete_pattern.match(u):
                        u = prefix + u
                        commercial_seed.add(u)
        '''
        commercial_reg = {ur'http://www\.881903\.com/.+detail.*'}
        spider_commercial = SpiderCommercialRadio('SpiderCommercialRadio', commercial_seed, commercial_reg, THREAD_NUM=10)
        spider_commercial.BATCH_NUMBER = util.get_day_stamp() + 10260
        spider_commercial.OFFSET = offset
        # spider_commercial.MAX_DEPTH = 5
        return spider_commercial


if __name__ == '__main__':

    SpiderCommercialRadio.PUT_IN_STORAGE = False
    SpiderCommercialRadio.start_crawling()
