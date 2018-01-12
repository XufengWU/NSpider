# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import re


class SpiderCool3C(common_news_spider.CommonNewsSpider):

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1'})
        t = doc('meta[property="article:published_time"]').attr('content')
        if t:
            t_stamp = util.get_timestamp_from_string(t) + 8 * 3600
        else:
            t_stamp = 0
        category = doc('a span[itemprop="name"]').text()
        author = doc('div.author span').text()
        content = util.get_paragraphs_from_selector(doc, 'article.article p')
        if content == '':
            content = doc('#lucy_box').text()

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'Cool3C'
        item.task_no = self.BATCH_NUMBER
        for img in doc('article.article img').items():
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
        cool_seed = {'https://www.cool3c.com/'}
        cool_reg = {ur'https\://www\.cool3c\.com/article/\d+'}
        spider_cool = SpiderCool3C('SpiderCool3C',
                                     cool_seed,
                                     cool_reg,
                                     THREAD_NUM=10,
                                     MAX_DEPTH=1)
        spider_cool.BATCH_NUMBER = util.get_day_stamp() + 10770
        spider_cool.OFFSET = offset
        return spider_cool


if __name__ == '__main__':
    SpiderCool3C.PUT_IN_STORAGE = False
    SpiderCool3C.start_crawling()
