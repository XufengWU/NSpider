# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
from pyquery import PyQuery as pq


article_prefix = u'http://hk.crntt.com/crn-webapp/doc/docDetail.jsp'
complete_pattern = re.compile(ur'http://.+')
full_doc_id_pattern = re.compile(ur'\?coluid=\d+&kindid=\d+&docid=\d+')
date_pattern = re.compile(ur'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
doc_id_pattern = re.compile(ur'docid=\d+')


class SpiderCRN(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u) and full_doc_id_pattern.findall(u):
                u = article_prefix + full_doc_id_pattern.findall(u)[0]
        else:
            u = ''
        if doc_id_pattern.findall(u):
            u = re.sub(ur'coluid=\d+', u'', u)
            u = re.sub(ur'kindid=\d+', u'', u)
            u = re.sub(ur'&', u'', u)
        return u

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if doc('td'):
                    t = util.get_time_string_from_selectors(doc, {'td'}, {date_pattern})
                    t_stamp = util.get_timestamp_from_string(t, '%Y-%m-%d %H:%M:%S')
                    if t_stamp >= util.get_month_day_timestamp(self.OFFSET):
                        return True
                    return False
                return False
        return False

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if not reg_pattern.match(doc_url):
                    return True
                elif doc('td'):
                    t = util.get_time_string_from_selectors(doc, {'td'}, {date_pattern})
                    t_stamp = util.get_timestamp_from_string(t, '%Y-%m-%d %H:%M:%S')
                    if t_stamp >= util.get_month_day_timestamp(self.OFFSET):
                        return True
                    return False
                return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, u'中國評論新聞：')
        t = util.get_time_string_from_selectors(doc, {'td'}, {date_pattern})
        t_stamp = util.get_timestamp_from_string(t, '%Y-%m-%d %H:%M:%S')
        category = ''
        scripts = doc('script').text()
        if re.findall(ur'coluid=\d+', task.url):
            col_id_str = re.findall(ur'coluid=\d+', task.url)[0]
            cat_block = re.findall(r'<a[^<>]*?' + col_id_str + '.+?</a>', scripts)[-1]
            cat_doc = pq(cat_block)
            category = cat_doc.text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, '#zoom')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'CRN'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        crn_seed = {'http://hk.crntt.com/crn-webapp/spec/195/index.jsp'}
        '''
        util.add_hrefs(url='http://hk.crntt.com/crn-webapp/spec/195/index.jsp',
                       selectors={'td[align=right a]'},
                       seeds=crn_seed,
                       seed_patterns={re.compile(ur'.*/kindOutline\.jsp\?coluid=\d+&kindid=\d+')})
        '''
        spider_crn = SpiderCRN('SpiderCRN', crn_seed, {ur'.*docid=\d+.*'}, THREAD_NUM=10)
        spider_crn.BATCH_NUMBER = util.get_day_stamp() + 10170
        spider_crn.OFFSET = offset
        return spider_crn


if __name__ == '__main__':

    SpiderCRN.PUT_IN_STORAGE = False
    SpiderCRN.start_crawling()
