# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
from pyquery import PyQuery as pq


prefix = u'http://www2.finet.hk'
complete_pattern = re.compile(ur'(http|https)://.+')
blank_pattern = re.compile(ur'[\s\n\t\r]+')


class SpiderFinet(common_news_spider.CommonNewsSpider):

    def get_doc(self, response):
        try:
            text = response.text
            text = re.sub(ur'[\s\t]*<!DOCTYPE', ur'<!DOCTYPE', text)
            if not blank_pattern.match(text):
                return pq(text)
            else:
                return pq('<html></html>')
        except Exception, e:
            raise e

    def get_url_of_link(self, link, doc, doc_url):
        u = ''
        if link.attr('href'):
            u = link.attr('href')
            if not complete_pattern.match(u):
                u = prefix + u
        return u

    def page_filter(self, doc, url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if doc('h6'):
                    t = util.get_time_string_from_selectors(doc, {'h6'})
                    t_stamp = 0
                    if re.findall(ur'上午', t):
                        t_stamp = util.get_timestamp_from_string(re.sub(ur'上午', u'AM', t), u'%Y年%m月%d日 %p%I:%M')
                    elif re.findall(ur'下午', t):
                        t_stamp = util.get_timestamp_from_string(re.sub(ur'下午', u'PM', t), u'%Y年%m月%d日 %p%I:%M')
                    if t_stamp >= util.get_day_stamp(offset=self.OFFSET):
                        return True
        return wanted

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if doc('h6'):
                    t = util.get_time_string_from_selectors(doc, {'h6'})
                    t_stamp = 0
                    if re.findall(ur'上午', t):
                        t_stamp = util.get_timestamp_from_string(re.sub(ur'上午', u'AM', t), u'%Y年%m月%d日 %p%I:%M')
                    elif re.findall(ur'下午', t):
                        t_stamp = util.get_timestamp_from_string(re.sub(ur'下午', u'PM', t), u'%Y年%m月%d日 %p%I:%M')
                    if t_stamp >= util.get_day_stamp(offset=self.OFFSET):
                        return True
                    return False
                return True
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        item.raw = doc.text()
        item.title = util.get_filtered_title(doc, {'h1'})
        item.t = util.get_time_string_from_selectors(doc, {'h6'})
        item.t_stamp = 0
        if re.findall(ur'上午', item.t):
            item.t_stamp = util.get_timestamp_from_string(re.sub(ur'上午', u'AM', item.t), u'%Y年%m月%d日 %p%I:%M')
        elif re.findall(ur'下午', item.t):
            item.t_stamp = util.get_timestamp_from_string(re.sub(ur'下午', u'PM', item.t), u'%Y年%m月%d日 %p%I:%M')
        item.fetched_at = task.fetched_at
        item.category = u'財經'
        item.author = ''
        content = util.get_paragraphs_from_selector(doc, 'div.newsContent p')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, 'div.newsContent div')
        content = re.sub(ur'(更多精彩內容.*|掃一掃.*)', u'', content)
        item.content = content
        item.url = task.url
        item.source = 'Finet'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        finet_seed = {'http://www2.finet.hk/'}
        util.add_hrefs(url='http://www2.finet.hk/',
                       selectors={'#mainmenu2 li a'},
                       seeds=finet_seed)
        finet_reg = {ur'http://www2\.finet\.hk/Newscenter/news_detail/.+'}
        spider_finet = SpiderFinet('SpiderFinet', finet_seed, finet_reg, THREAD_NUM=10)
        spider_finet.BATCH_NUMBER = util.get_day_stamp() + 10250
        spider_finet.OFFSET = offset
        return spider_finet


if __name__ == '__main__':

    SpiderFinet.PUT_IN_STORAGE = False
    SpiderFinet.start_crawling()
