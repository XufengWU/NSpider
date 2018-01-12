# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import requests
from pyquery import PyQuery as pq


class SpiderUBeat(common_news_spider.CommonNewsSpider):

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1'})
        t = doc('meta[property="article:published_time"]').attr('content')
        t_stamp = 0
        if t:
            t_stamp = util.get_timestamp_from_string(t)
        category = ''
        author = ''
        content = util.get_paragraphs_from_selector(doc, '#main-content .entry-content p')
        content = re.sub(ur'繼續閱讀[\n\s\S.]*', '', content)

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'UBeat'
        item.task_no = self.BATCH_NUMBER
        for img in doc('figure.entry-thumbnail img').items():
            if img.attr('src') != '':
                media_u = img.attr('src')
                des = ''
                if img.attr('alt'):
                    des = img.attr('alt')
                media = self.NewsItem.MediaItem(media_url=media_u, type='image', description=des,
                                                created_at=item.fetched_at)
                item.media_list.append(media)

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        ubeat_seed = {'http://ubeat.com.cuhk.edu.hk/'}
        # day_str = util.get_day_string(offset=offset)
        spider_ubeat = SpiderUBeat('SpiderUBeat',
                               ubeat_seed,
                               {ur'http://ubeat\.com\.cuhk\.edu\.hk/\d+.+', ur'http://ubeat\.com\.cuhk\.edu\.hk/mm_.+'},
                               THREAD_NUM=5)
        spider_ubeat.OFFSET = offset
        spider_ubeat.BATCH_NUMBER = util.get_day_stamp() + 10630
        return spider_ubeat

if __name__ == '__main__':
    SpiderUBeat.PUT_IN_STORAGE = False
    SpiderUBeat.ADD_MEDIA = True
    SpiderUBeat.start_crawling()
