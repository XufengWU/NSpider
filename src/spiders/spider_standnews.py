# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time
import requests
from pyquery import PyQuery as pq


w_pattern = re.compile(ur'/\w+/.+')
cat_pattern = re.compile(ur'(?<=\.com)/.*?/(?=.*)')
ad_image_pattern = re.compile(r'.*ad-placeholder.*')
youtube_pattern = re.compile(r'.*youtube.*')


class SpiderStand(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = ''
        if link.attr('href'):
            u = link.attr('href').encode('utf-8')
            if w_pattern.match(u):
                u = 'http://www.thestandnews.com' + u
        return u

    def page_filter(self, doc, url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if doc('div.article-content-wrap p.date'):
                    tm_day = time.localtime().tm_mday
                    search_offset = self.OFFSET
                    if tm_day > search_offset:
                        tm_day -= search_offset
                    else:
                        tm_day = 1
                    current_date = str(time.localtime().tm_year) + ('%02d' % time.localtime().tm_mon) + ('%02d' % tm_day)
                    # the timestamp of current date
                    t_stamp = int(time.mktime(time.strptime(current_date, '%Y%m%d')))
                    if int(time.mktime(time.strptime(doc('div.article-content-wrap p.date').text().encode('utf-8'),
                                                     "%Y/%m/%d — %H:%M"))) >= t_stamp:
                        wanted = True
        return wanted

    def task_filter(self, doc, url, doc_url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if doc('div.article-content-wrap p.date').text():
                    tm_day = time.localtime().tm_mday
                    search_offset = self.OFFSET
                    if tm_day > search_offset:
                        tm_day -= search_offset
                    else:
                        tm_day = 1
                    current_date = str(time.localtime().tm_year) + ('%02d' % time.localtime().tm_mon) + ('%02d' % tm_day)
                    # the timestamp of current date
                    t_stamp = int(time.mktime(time.strptime(current_date, '%Y%m%d')))
                    if int(time.mktime(time.strptime(doc('div.article-content-wrap p.date').text().encode('utf-8'),
                                                     "%Y/%m/%d — %H:%M"))) >= t_stamp:
                        wanted = True
                else:
                    wanted = True
        return wanted

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, ur'\s*\|.*')
        t = doc('div.article-content-wrap p.date').text()
        t_stamp = int(time.mktime(time.strptime(t.encode('utf-8'), '%Y/%m/%d — %H:%M')))
        cat_href = cat_pattern.findall(task.url)[0]
        category = doc('ul[id=mainMenuUL] a[href="' + cat_href + '"]').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc.remove('style'), 'div.article-content p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'StandNews'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.article-content-wrap img').items():
            if img.attr('src') != '' and not ad_image_pattern.match(img.attr('src')):
                des = ''
                if img.attr('alt'):
                    des = img.attr('alt')
                media = self.NewsItem.MediaItem(media_url=img.attr('src'), type='image', description=des, created_at = item.fetched_at)
                item.media_list.append(media)
        for iframe in doc('.article-content-wrap iframe').items():
            if iframe.attr('src') and youtube_pattern.match(iframe.attr('src')):
                media = self.NewsItem.MediaItem(media_url=iframe.attr('src'), type='youtube', description='youtube', created_at=item.fetched_at)
                item.media_list.append(media)
        if util.within_active_interval(6, 1200):
            _comments = util.get_filtered_facebook_comments_data('1534089350179685',
                                                                 doc('div.fb-comments').attr('data-href'), task.url)
            if _comments:
                for _comment in _comments:
                    item.media_list.append(
                        self.NewsItem.MediaItem(media_url=_comment['json_string'], type='comments',
                                                description='comments', created_at=item.fetched_at)
                    )

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        st_seed = {'https://www.thestandnews.com/'}
        st_index = pq(requests.get('https://www.thestandnews.com/'))
        cat_list = st_index('ul[id=mainMenuUL] a').items()
        short_pattern = re.compile(ur'/.*/')
        for cat in cat_list:
            if short_pattern.match(cat.attr('href')):
                st_seed.add('http://www.thestandnews.com' + cat.attr('href'))
        spider_stand = SpiderStand('SpiderStand', st_seed, {ur'http://www\.thestandnews\.com/(?!author)\w+?/.{20,}'},
                                   THREAD_NUM=10)
        spider_stand.OFFSET = offset
        spider_stand.BATCH_NUMBER = util.get_day_stamp() + 10005
        return spider_stand


if __name__ == '__main__':

    SpiderStand.PUT_IN_STORAGE = False
    SpiderStand.start_crawling()
