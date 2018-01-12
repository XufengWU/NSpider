# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import re


class SpiderTMHK(common_news_spider.CommonNewsSpider):

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1'})
        t = doc('meta[property="article:published_time"]').attr('content')
        if t:
            t_stamp = util.get_timestamp_from_string(t)
        else:
            t_stamp = 0
        category = doc('.single-meta div:nth-child(3) a').text()
        author = doc('.single-meta span.author.vcard').text()
        if len(author) > 20:
            author = ''
        content = util.get_paragraphs_from_selector(doc, 'div.resize p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'TMHK'
        item.task_no = self.BATCH_NUMBER
        for img in doc('div.resize img').items():
            if img.attr('src') != '':
                media_u = img.attr('src')
                des = ''
                if img.attr('alt'):
                    des = img.attr('alt')
                elif img.siblings('p'):
                    des = img.siblings('p').text()
                media = self.NewsItem.MediaItem(media_url=media_u, type='image', description=des,
                                                created_at=item.fetched_at)
                item.media_list.append(media)

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        tmhk_seed = {'http://tmhk.org/',
                     'http://tmhk.org/category/%E6%94%BF%E6%B2%BB/',
                     'http://tmhk.org/category/%E8%B2%A1%E7%B6%93/',
                     'http://tmhk.org/category/%E7%A4%BE%E6%9C%83/',
                     'http://tmhk.org/category/%E7%94%9F%E6%B4%BB/'}
        tmhk_reg = {ur'http\://tmhk\.org/\d{4}/\d\d/.+'}
        spider_tmhk = SpiderTMHK('SpiderTMHK',
                                 tmhk_seed,
                                 tmhk_reg,
                                 THREAD_NUM=10,
                                 MAX_DEPTH=1)
        spider_tmhk.BATCH_NUMBER = util.get_day_stamp() + 10740
        spider_tmhk.OFFSET = offset
        return spider_tmhk


if __name__ == '__main__':

    SpiderTMHK.PUT_IN_STORAGE = False
    SpiderTMHK.start_crawling()
