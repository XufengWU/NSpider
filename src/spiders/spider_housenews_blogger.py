# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import re

complete_pattern = re.compile(r'http://.+')
news_prefix = 'https://thehousenewsbloggers.net/'
stop_pattern = re.compile(r'share=|#respond')


class SpiderHouseNewsBlogger(common_news_spider.CommonNewsSpider):

    def task_filter(self, doc, url, doc_url):
        for pattern in self.reg_patterns:
            if pattern.match(url):
                if not stop_pattern.findall(url):
                    return True
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1'})
        # pl = doc('.heading .pull-left')
        # pl.remove('span')
        t = doc('meta[property="article:published_time"]').attr('content')
        if t:
            t_stamp = util.get_timestamp_from_string(t)
        else:
            t_stamp = 0
        category = doc('.post-lead-category').text()
        author = doc('.author.vcard').text()
        content = util.get_paragraphs_from_selector(doc, 'section.entry p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'HouseNewsBlogger'
        item.task_no = self.BATCH_NUMBER
        for img in doc('section.entry img').items():
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
        for a in doc('iframe').items():
            if a.attr('src') and re.match(r'.*youtube\.com.+', a.attr('src')):
                media_u = a.attr('src')
                if re.match(r'//.+', media_u):
                    media_u = 'http:' + media_u
                media = self.NewsItem.MediaItem(media_url=media_u, type='youtube', description='youtube',
                                                created_at=item.fetched_at)
                item.media_list.append(media)

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        housenewsblogger_seed = {'https://thehousenewsbloggers.net/'}
        housenewsblogger_reg = {ur'https://thehousenewsbloggers.net/'+util.get_day_string('/', offset=offset)+u'/.+'}
        spider_housenewsblogger = SpiderHouseNewsBlogger('SpiderHouseNewsBlogger',
                                                         housenewsblogger_seed,
                                                         housenewsblogger_reg,
                                                         THREAD_NUM=10,
                                                         MAX_DEPTH=2)
        spider_housenewsblogger.BATCH_NUMBER = util.get_day_stamp() + 10760
        spider_housenewsblogger.OFFSET = offset
        return spider_housenewsblogger


if __name__ == '__main__':
    SpiderHouseNewsBlogger.PUT_IN_STORAGE = False
    SpiderHouseNewsBlogger.start_crawling(offset=0)
