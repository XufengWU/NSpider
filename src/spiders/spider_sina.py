# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time


complete_pattern = re.compile(ur'http://sina\.com\.hk/.*')
cat_pattern = re.compile(ur'(?<=unikeyword=\').*?(?=\')')
ad_url_pattern = re.compile(ur'ad\.sinahk.+')


class SpiderSina(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        prefix = 'http://sina.com.hk'
        if u is not None:
            if not complete_pattern.match(u):
                u = prefix + u
        else:
            u = ''
        return u

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, ur' - 香港新浪')
        t = doc('div.news-datetime').text()
        t_stamp = int(time.mktime(time.strptime(t.encode('utf-8'), '%Y年%m月%d日 %H:%M')))
        scripts = doc('script').text()
        category = ''
        if re.findall(cat_pattern, scripts):
            category = re.findall(cat_pattern, scripts)[0]
        author = ''
        content = util.get_paragraphs_from_selector(doc, 'div.news-body p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'Sina'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.news-body img').items():
            if img.attr('src') != '':
                media_u = img.attr('src')
                if not ad_url_pattern.findall(media_u):
                    des = ''
                    if img.parent().attr('data-caption'):
                        des = img.parent().attr('data-caption')
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
        if util.within_active_interval(6, 1200):
            _comments = util.get_filtered_facebook_comments_data('114907575364430',
                                                                 doc('div.fb-comments').attr('data-href'), task.url)
            if _comments:
                for _comment in _comments:
                    item.media_list.append(
                        self.NewsItem.MediaItem(media_url=_comment['json_string'], type='comments',
                                                description='comments', created_at=item.fetched_at)
                    )

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        sina_seed = {'http://sina.com.hk/news/'}
        spider_sina = SpiderSina(name='SpiderSina', seed_urls=sina_seed,
                                 regs={ur'http://sina.com.hk/.*/article/' + util.get_day_string(offset=offset) + ur'/.*'},
                                 THREAD_NUM=10)
        spider_sina.BATCH_NUMBER = util.get_day_stamp() + 10070
        spider_sina.OFFSET = offset
        return spider_sina


if __name__ == '__main__':

    SpiderSina.PUT_IN_STORAGE = False
    SpiderSina.start_crawling()
