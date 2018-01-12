# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time

relative_hour_pattern = re.compile(ur'\d+\s*小時前')


class Spider730Column(common_news_spider.CommonNewsSpider):

    def normal_item_solver(self, item, task, response):
        doc = self.get_doc(response)

        title = doc('.news-detail-container .news-detail-title').text()
        t = doc('.news-detail-date').text()
        t_stamp = util.get_timestamp_from_string(t)
        if relative_hour_pattern.match(t):
            t_stamp = int(time.time()) - int(re.findall(r'\d+', t)[0]) * 3600
        category = u'專欄'
        author = doc('.category-title').text()
        content = util.get_paragraphs_from_selector(doc, '.news-detail-content p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'AM730 Column'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        _730_column_seed = {u'https://www.am730.com.hk/column/%E6%96%B0%E8%81%9E',
                            u'https://www.am730.com.hk/column/%E8%B2%A1%E7%B6%93',
                            u'https://www.am730.com.hk/column/%E7%A7%91%E6%8A%80'}
        spider_730_column = Spider730Column('Spider730Column',
                                            _730_column_seed,
                                            {ur'https://www\.am730\.com\.hk/column/%E6%96%B0%E8%81%9E/.+',
                                             u'https://www\.am730\.com\.hk/column/%E8%B2%A1%E7%B6%93/.+',
                                             u'https://www\.am730\.com\.hk/column/%E7%A7%91%E6%8A%80/.+'},
                                            THREAD_NUM=5)
        spider_730_column.OFFSET = offset
        spider_730_column.BATCH_NUMBER = util.get_day_stamp() + 10640
        return spider_730_column


if __name__ == '__main__':
    Spider730Column.PUT_IN_STORAGE = False
    Spider730Column.start_crawling()
