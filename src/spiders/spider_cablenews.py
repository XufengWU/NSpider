# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import re

date_pattern = re.compile(r'\d\d\d\d/\d\d/\d\d \d\d:\d\d')


class SpiderCableNews(common_news_spider.CommonNewsSpider):

    def page_filter(self, doc, url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if doc('div.video_date span'):
                    t = util.get_time_string_from_selectors(doc, {'div.video_date span'}, date_patterns={date_pattern})
                    t_stamp = util.get_timestamp_from_string(t)
                    if t_stamp >= util.get_day_stamp(self.OFFSET):
                        return True
        return wanted

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if doc('div.video_date span'):
                    t = util.get_time_string_from_selectors(doc, {'div.video_date span'}, date_patterns={date_pattern})
                    t_stamp = util.get_timestamp_from_string(t)
                    if t_stamp >= util.get_day_stamp(self.OFFSET):
                        return True
                    return False
                return True
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'})
        t = util.get_time_string_from_selectors(doc, {'div.video_date span'}, date_patterns={date_pattern})
        t_stamp = util.get_timestamp_from_string(t) + int(time.localtime().tm_sec)
        category = doc('span.heretxt').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, 'div.video_content')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'CableNews'
        item.task_no = self.BATCH_NUMBER
        if util.within_active_interval(6, 1200):
            _comments = util.get_filtered_facebook_comments_data('482092838576644',
                                                                 doc('div.fb-comments').attr('data-href'), task.url)
            if _comments:
                for _comment in _comments:
                    item.media_list.append(
                        self.NewsItem.MediaItem(media_url=_comment['json_string'], type='comments',
                                                description='comments', created_at=item.fetched_at)
                    )

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        cablenews_seed = {'http://cablenews.i-cable.com/webapps/index/index.php'}
        util.add_hrefs('http://cablenews.i-cable.com/webapps/index/index.php', {'#header_web_chi a'}, cablenews_seed)
        cablenews_reg = {ur'http://.+?\.i-cable\.com/.*videopage.*\d+/.*'}
        spider_cablenews = SpiderCableNews('SpiderCableNews',
                                           cablenews_seed,
                                           cablenews_reg,
                                           THREAD_NUM=10)
        spider_cablenews.BATCH_NUMBER = util.get_day_stamp() + 10220
        spider_cablenews.OFFSET = offset
        return spider_cablenews


if __name__ == '__main__':

    SpiderCableNews.PUT_IN_STORAGE = False
    SpiderCableNews.start_crawling()
