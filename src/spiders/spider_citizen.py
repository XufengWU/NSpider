# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import re

complete_pattern = re.compile(r'http://.+')
news_prefix = 'http://www.hkcnews.com'


class SpiderCitizen(common_news_spider.CommonNewsSpider):
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
        info = doc('.article-info').text()
        t = info.split(' | ')[-1]
        if t:
            t_stamp = util.get_timestamp_from_string(t)
            if t.find(u'發佈日期') >= 0:
                t_stamp = util.get_timestamp_from_string(t,
                                                         u'發佈日期: %d.%m.%y') + time.localtime().tm_hour * 3600 + time.localtime().tm_min * 60
            elif t.find(u'Publish Date') >= 0:
                t_stamp = util.get_timestamp_from_string(t,
                                                         u'Publish Date: %d.%m.%y') + time.localtime().tm_hour * 3600 + time.localtime().tm_min * 60
        else:
            t_stamp = 0
        category = doc('.group').text()
        author = re.findall(ur'(?<=撰文: ).+?(?= \|)', info)
        if author:
            author = author[0]
        else:
            author = ''
        content = util.get_paragraphs_from_selector(doc.remove('script'), '.article-content p,h2:not(.hidden)')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'CitizenNews'
        item.task_no = self.BATCH_NUMBER
        for fig in doc('.article-content figure.image').items():
            img = fig('img')
            if img and img.attr('src') != '':
                media_u = img.attr('src')
                if not complete_pattern.match(media_u):
                    media_u = news_prefix + media_u
                des = ''
                if fig('figcaption'):
                    des = fig('figcaption').text()
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
        citizen_seed = {'https://www.hkcnews.com/'}
        citizen_reg = {ur'http\://www\.hkcnews\.com/article/\d+/.+'}
        spider_citizen = SpiderCitizen('SpiderCitizen',
                                       citizen_seed,
                                       citizen_reg,
                                       THREAD_NUM=10,
                                       MAX_DEPTH=1)
        spider_citizen.BATCH_NUMBER = util.get_day_stamp() + 10780
        spider_citizen.OFFSET = offset
        return spider_citizen


if __name__ == '__main__':
    SpiderCitizen.PUT_IN_STORAGE = False
    SpiderCitizen.start_crawling()
