# -*- coding:utf-8 -*-
import common_news_spider
import util
import re

complete_pattern = re.compile(ur'http://.+')
news_prefix = 'http://www.hkcna.hk/'
date_patterns = {re.compile(ur'\d{4}年\d\d月\d\d日 \d\d:\d\d')}


class SpiderHKCNA(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = news_prefix + u
        else:
            u = ''
        return u

    def normal_item_solver(self, item, task, response):

        response.encoding = 'utf-8'
        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'})
        t = util.get_time_string_from_selectors(doc, {'.tm'}, date_patterns)
        t_stamp = util.get_timestamp_from_string(t)
        category = (doc('h2 b').text())[:-2]
        author = doc('.fdr span').text()
        content = util.get_paragraphs_from_selector(doc, '.wz_nr p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'HKCNA'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        bbc_seed = {'http://www.hkcna.hk/'}
        util.add_hrefs('http://www.hkcna.hk/', {'.baner_01 a'}, bbc_seed, news_prefix)
        day_str = util.get_day_string(offset=offset)
        day_str = day_str[:4] + '/' + day_str[4:]
        spider_hkcna = SpiderHKCNA('SpiderHKCNA',
                                   bbc_seed,
                                   {ur'http://www.hkcna.hk/.+' + day_str + '.+'},
                                   THREAD_NUM=5)
        spider_hkcna.OFFSET = offset
        spider_hkcna.BATCH_NUMBER = util.get_day_stamp() + 10370
        return spider_hkcna


if __name__ == '__main__':
    SpiderHKCNA.PUT_IN_STORAGE = False
    SpiderHKCNA.start_crawling()
