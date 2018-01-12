# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time


complete_pattern = re.compile(ur'http://.+')


class SpiderPeople(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                day_str = util.get_day_string('-', offset=self.OFFSET)
                day_str = day_str[:-3] + '/' + day_str[-2:]
                u = 'http://paper.people.com.cn/rmrbhwb/html/' + day_str + '/' + u
        else:
            u = ''
        return u

    def normal_item_solver(self, item, task, response):

        response.encoding = 'utf-8'
        doc = self.get_doc(response)

        title = doc('h1').text()
        t = util.get_day_string(offset=self.OFFSET)
        t_stamp = util.get_timestamp_from_string(t, time_format='%Y%m%d') + time.localtime().tm_hour*3600 + time.localtime().tm_min*60
        category = re.split(r'[:\s]', doc('.ban_t li').text())[1]
        author = ''
        content = util.get_paragraphs_from_selector(doc, '#ozoom p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'People'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        day_str = util.get_day_string('-', offset=offset)
        day_str = day_str[:-3] + '/' + day_str[-2:]
        people_seed = set()
        for i in range(12):
            people_seed.add('http://paper.people.com.cn/rmrbhwb/html/' + day_str + '/node_' + str(865+i) + '.htm')
        spider_people = SpiderPeople('SpiderPeople',
                                     people_seed,
                                     {ur'http://paper\.people\.com\.cn/rmrbhwb/html/.*/content_\d+\.htm'},
                                     THREAD_NUM=5)
        spider_people.OFFSET = offset
        spider_people.BATCH_NUMBER = util.get_day_stamp() + 10580
        return spider_people


if __name__ == '__main__':
    SpiderPeople.PUT_IN_STORAGE = False
    SpiderPeople.start_crawling()
