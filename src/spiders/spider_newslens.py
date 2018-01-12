# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import re

complete_pattern = re.compile(r'http://.+')


class SpiderNewsLens(common_news_spider.CommonNewsSpider):
    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, u' - The News Lens.*')
        t = doc('meta[property="article:published_time"]').attr('content')
        t_stamp = util.get_timestamp_from_string(t) + 8 * 3600
        category = doc('meta[property="article:section"]').attr('content')
        author = doc('meta[name="author"]').attr('content')
        content = util.get_paragraphs_from_selector(doc, 'div.article-body-container div.article-content p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'NewsLens'
        item.task_no = self.BATCH_NUMBER
        for img in doc(
                'div.article-header-container img.front-img, div.article-content img').items():
            if img and img.attr('src') != '':
                media_u = img.attr('src-lg')
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
        newslens_seed = {'https://www.thenewslens.com/', 'https://hk.thenewslens.com/',
                         'https://international.thenewslens.com/', 'https://asean.thenewslens.com/'}
        newslens_reg = {ur'https\://\w+?\.thenewslens\.com/article/\d+.+'}
        spider_newslens = SpiderNewsLens('SpiderNewsLens',
                                         newslens_seed,
                                         newslens_reg,
                                         THREAD_NUM=10,
                                         MAX_DEPTH=1)
        spider_newslens.BATCH_NUMBER = util.get_day_stamp() + 10790
        spider_newslens.OFFSET = offset
        return spider_newslens


if __name__ == '__main__':
    SpiderNewsLens.PUT_IN_STORAGE = False
    SpiderNewsLens.ADD_MEDIA = True
    SpiderNewsLens.start_crawling()
