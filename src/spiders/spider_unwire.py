# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time


complete_pattern = re.compile(ur'http://.+')
date_pattern = re.compile(ur'\d{4}-\d\d-\d\d')
cat_pattern = re.compile(ur'(?<=/).[^/]+?(?=/$)')


class SpiderUnwire(common_news_spider.CommonNewsSpider):

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = doc('meta[property="article:published_time"]').attr('content')
                t_stamp = 0
                if t:
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
                t = doc('meta[property="article:published_time"]').attr('content')
                t_stamp = 0
                if t:
                    t_stamp = util.get_timestamp_from_string(t)
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1.entry-title'})
        t = doc('meta[property="article:published_time"]').attr('content')
        t_stamp = 0
        if t:
            t_stamp = util.get_timestamp_from_string(t)
        category = ''
        cat_find_res = cat_pattern.findall(task.url)
        if cat_find_res:
            category = cat_find_res[0]
        category = u'科技/' + category
        author = ''
        content = util.get_paragraphs_from_selector(doc, '#content div.entry p:not(.meta)')
        content = re.sub(ur'(來源：|來源:|Tags:).+', u'', content)

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'Unwire'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        unwire_seed = {'https://unwire.hk/articles/page/1/'}
        spider_unwire = SpiderUnwire('SpiderUnwire',
                                     unwire_seed,
                                     {ur'https\://unwire\.hk/\d{4}/\d\d/\d\d/.+'},
                                     THREAD_NUM=10, MAX_DEPTH=2)
        spider_unwire.BATCH_NUMBER = util.get_day_stamp() + 10680
        spider_unwire.OFFSET = offset
        return spider_unwire


if __name__ == '__main__':

    SpiderUnwire.PUT_IN_STORAGE = False
    SpiderUnwire.DEFAULT_PUT_IN_FILE = True
    for i in range(166, 186):
        _seed_urls = set()
        _seed_urls.add('https://unwire.hk/articles/page/'+str(i)+'/')
        SpiderUnwire.start_crawling(offset=100, seed_urls=_seed_urls, OUTPUT_FILE_PATH='Unwire_'+str(i)+'.json')
