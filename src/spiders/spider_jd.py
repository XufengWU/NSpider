# -*- coding:utf-8 -*-
import common_news_spider
import util
import re


complete_pattern = re.compile(ur'http://.+')
date_pattern = re.compile(ur'\d{4}-\d\d-\d\d')
prefix = 'http://www.jdonline.com.hk'


class SpiderJD(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = prefix + u[2:]
        else:
            u = ''
        u = re.sub(r'( |\')title=.*', '', u)
        return u

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = doc('.date').text()
                if date_pattern.findall(t):
                    t = date_pattern.findall(t)[0]
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
                t = doc('.date').text()
                if date_pattern.findall(t):
                    t = date_pattern.findall(t)[0]
                t_stamp = util.get_timestamp_from_string(t)
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def normal_item_solver(self, item, task, response):

        response.encoding = 'utf-8'
        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'.article-header h1'})
        t = doc('.date').text()
        if date_pattern.findall(t):
            t = date_pattern.findall(t)[0]
        t_stamp = util.get_timestamp_from_string(t)
        category = doc('.now-here').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, '.article p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'JD Online'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        jd_seed = {'http://www.jdonline.com.hk/index/index.php'}
        spider_jd = SpiderJD('SpiderJD',
                             jd_seed,
                             {ur'http://www\.jdonline\.com\.hk.+\?news_id=\d+.+'},
                             THREAD_NUM=10)
        spider_jd.BATCH_NUMBER = util.get_day_stamp() + 10540
        spider_jd.OFFSET = offset
        return spider_jd


if __name__ == '__main__':

    SpiderJD.PUT_IN_STORAGE = False
    SpiderJD.start_crawling()
