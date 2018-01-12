# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time


prefix = u'https://theinitium.com'
complete_pattern = re.compile(ur'(http|https)://.+')


class SpiderInitium(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = ''
        if link.attr('href'):
            u = link.attr('href')
            if not complete_pattern.match(u):
                u = prefix + u
        return u

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, ur'\|.*')
        t = util.get_time_string_from_selectors(doc, {'span.posted-time'})
        t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_hour*3600 + time.localtime().tm_min*60 + time.localtime().tm_sec
        category = doc('span.channel-section').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, 'div.article-content p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.redirected_url
        item.source = 'Initium'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.main-content .image img').items():
            if img.attr('src') != '':
                media_u = img.attr('src')
                if re.match(r'//.+', media_u):
                    media_u = 'http:' + media_u
                des = ''
                if img.attr('alt'):
                    des = img.attr('alt')
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
        initium_seed = {'https://theinitium.com/'}
        util.add_hrefs(url='https://theinitium.com/',
                       selectors={'div.left-nav-top li a'},
                       seeds=initium_seed,
                       prefix=prefix)
        initium_reg = {ur'https://theinitium\.com/article/' + util.get_day_string(offset=offset) + '-.+', ur'http://feeds\.initium.+'}
        spider_initium = SpiderInitium('SpiderInitium',
                                       initium_seed,
                                       initium_reg,
                                       THREAD_NUM=10)
        spider_initium.BATCH_NUMBER = util.get_day_stamp() + 10190
        spider_initium.OFFSET = offset
        return spider_initium


if __name__ == '__main__':

    SpiderInitium.PUT_IN_STORAGE = False
    SpiderInitium.start_crawling()
