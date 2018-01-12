# -*- coding:utf-8 -*-
import common_news_spider
import util


class Spider852(common_news_spider.CommonNewsSpider):

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = doc('.updated').text()
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
                t = doc('.updated').text()
                t_stamp = util.get_timestamp_from_string(t)
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = doc('h1').text()
        t = doc('.updated').text()
        t_stamp = util.get_timestamp_from_string(t)
        category = doc('.categories a:first-child').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, '.content.clearfix p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = '852'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        _852_seed = {'http://www.post852.com/'}
        util.add_hrefs('http://www.post852.com/', {'#rightnav a'}, _852_seed)
        spider_852 = Spider852('Spider852',
                               _852_seed,
                               {ur'http://www.post852.com/\d+/.+'},
                               THREAD_NUM=5)
        spider_852.OFFSET = offset
        spider_852.BATCH_NUMBER = util.get_day_stamp() + 10400
        return spider_852


if __name__ == '__main__':
    Spider852.PUT_IN_STORAGE = False
    Spider852.start_crawling()
