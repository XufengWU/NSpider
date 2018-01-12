# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import re
from pyquery import PyQuery as pq

complete_pattern = re.compile(r'http\://.+')
news_prefix = 'http://www.cnbc.com'


class SpiderCNBC(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = news_prefix + u
        else:
            u = ''
        return u

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1'})
        t = doc('meta[property="article:published_time"]').attr('content')
        if t:
            t_stamp = util.get_timestamp_from_string(t) + 8 * 3600
        else:
            t_stamp = 0
        category = doc('#pageHeadNav li.selected').text()
        author = doc('.story-top a[rel="author"]').text()
        content = util.get_paragraphs_from_selector(doc, '#article_body p')
        content = re.sub(r'Follow CNBC International on.+', '', content)

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'CNBC'
        item.task_no = self.BATCH_NUMBER
        for img in doc('#article_body img').items():
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
        cnbc_seed = {'http://www.cnbc.com/hong-kong/'}
        cnbc_reg = {ur'http://www.cnbc.com/'+util.get_day_string(interval_str='/', offset=offset)+u'/.+'}
        spider_cnbc = SpiderCNBC('SpiderCNBC',
                                 cnbc_seed,
                                 cnbc_reg,
                                 THREAD_NUM=10,
                                 MAX_DEPTH=2)
        spider_cnbc.BATCH_NUMBER = util.get_day_stamp() + 10730
        spider_cnbc.OFFSET = offset
        return spider_cnbc


if __name__ == '__main__':

    SpiderCNBC.PUT_IN_STORAGE = False
    SpiderCNBC.start_crawling()
