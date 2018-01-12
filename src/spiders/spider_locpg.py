# -*- coding:utf-8 -*-
import common_news_spider
import util


class SpiderLocpg(common_news_spider.CommonNewsSpider):

    def normal_item_solver(self, item, task, response):

        response.encoding = 'utf-8'
        doc = self.get_doc(response)

        title = doc('h1').text()
        t = util.get_day_string(offset=self.OFFSET)
        t_stamp = util.get_now()
        category = ''
        author = ''
        content = util.get_paragraphs_from_selector(doc, '#content p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'Locpg'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        locpg_seed = {'http://www.locpg.gov.cn/', 'http://www.locpg.hk/zxzx/xzdt.htm'}
        day_str = util.get_day_string('-', offset=offset)
        day_str = day_str[0:-3] + '/' + day_str[-2:]
        spider_locpg = SpiderLocpg('SpiderLocpg',
                                   locpg_seed,
                                   {ur'http://www.locpg.hk/.+' + day_str + '.+'},
                                   THREAD_NUM=5)
        spider_locpg.OFFSET = offset
        spider_locpg.BATCH_NUMBER = util.get_day_stamp() + 10350
        return spider_locpg


if __name__ == '__main__':
    SpiderLocpg.PUT_IN_STORAGE = False
    SpiderLocpg.start_crawling()

