# -*- coding: utf-8 -*-
import common_news_spider
import util
import re
import requests
import time
from pyquery import PyQuery as pq

article_pattern = re.compile(ur'/article/.*')
full_article_pattern = re.compile(ur'(?<=http://www\.passiontimes\.hk/article/).*?(?=/)')


class SpiderPt(common_news_spider.CommonNewsSpider):
    def get_url_of_link(self, link, doc, doc_url):
        href = link.attr('href')
        if href and article_pattern.match(href):
            return 'http://www.passiontimes.hk' + href
        return href

    def page_filter(self, doc, url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = full_article_pattern.findall(url)[0]
                if util.get_timestamp_from_string(t, '%m-%d-%Y') >= util.get_day_stamp(offset=self.OFFSET):
                    wanted = True
        return wanted

    def task_filter(self, doc, url, doc_url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = full_article_pattern.findall(url)[0]
                if util.get_timestamp_from_string(t, '%m-%d-%Y') >= util.get_day_stamp(offset=self.OFFSET):
                    wanted = True
        return wanted

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, ur'熱血時報 \| ')
        author = doc('span.author a').text()
        t = doc('time[class="published"]').text()
        t_stamp = int(time.mktime(time.strptime(str(doc('time[class="published"]').text()), "%m-%d-%Y")))
        category = doc('div.page-path a').text()
        doc.remove('script')
        doc.remove('style')
        content = util.get_paragraphs_from_selector(doc, 'div.article-body p')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, 'div.article-body')
        if t_stamp >= int(time.mktime(time.strptime(str(time.localtime().tm_year) + str(time.localtime().tm_mon) + str(
                time.localtime().tm_mday), '%Y%m%d'))):
            t_stamp = int(time.time())

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'PassionTimes'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.article-body img').items():
            if img.attr('src') != '':
                media_u = img.attr('src')
                if re.match(r'//.+', media_u):
                    media_u = 'http:' + media_u
                elif not re.match(r'http://.+', media_u):
                    media_u = 'http://www.passiontimes.hk' + media_u
                media = self.NewsItem.MediaItem(media_url=media_u, type='image', description='',
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
            _comments = util.get_filtered_facebook_comments_data('462543587117177',
                                                                 doc('div.fb-comments').attr('data-href'), task.url)
            if _comments:
                for _comment in _comments:
                    item.media_list.append(
                        self.NewsItem.MediaItem(media_url=_comment['json_string'], type='comments',
                                                description='comments', created_at=item.fetched_at)
                    )

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        # pt_index = pq(requests.get('http://www.passiontimes.hk/4.0/index.php').text)
        # pt_seed = set([])
        # cat_pattern = re.compile(ur'/4.0/category/.*')
        # for cat in pt_index('div.footer-siteMap a').items():
        #     if cat_pattern.match(cat.attr('href').encode('utf-8')):
        #         pt_seed.add('http://www.passiontimes.hk' + str(cat.attr('href')))
        pt_seed = {
            'http://www.passiontimes.hk/4.0/index.php',
            'http://www.passiontimes.hk/4.0/category/3/19',
            'http://www.passiontimes.hk/4.0/category/1/5',
            'http://www.passiontimes.hk/4.0/category/1/4',
            'http://www.passiontimes.hk/4.0/category/1/7',
            'http://www.passiontimes.hk/4.0/category/2/62',
            'http://www.passiontimes.hk/4.0/category/1/1',
            'http://www.passiontimes.hk/4.0/category/1/3',
            'http://www.passiontimes.hk/4.0/category/1/2',
            'http://www.passiontimes.hk/4.0/category/1/6',
            'http://www.passiontimes.hk/4.0/category/2/18',
            'http://www.passiontimes.hk/4.0/category/2/14',
            'http://www.passiontimes.hk/4.0/category/2/15',
            'http://www.passiontimes.hk/4.0/category/2/16',
            'http://www.passiontimes.hk/4.0/category/2/17',
            'http://www.passiontimes.hk/4.0/category/2/10',
            'http://www.passiontimes.hk/4.0/category/2/11',
            'http://www.passiontimes.hk/4.0/category/2/12',
            'http://www.passiontimes.hk/4.0/category/2/13',
            'http://www.passiontimes.hk/4.0/category/2/8',
            'http://www.passiontimes.hk/4.0/category/2/9',
            'http://www.passiontimes.hk/4.0/category/3/125',
            'http://www.passiontimes.hk/4.0/category/1/37',
            'http://www.passiontimes.hk/4.0/category/2/135',
            'http://www.passiontimes.hk/4.0/category/1/124',
            'http://www.passiontimes.hk/4.0/category/3/22',
            'http://www.passiontimes.hk/4.0/category/3/23',
            'http://www.passiontimes.hk/4.0/category/3/20',
            'http://www.passiontimes.hk/4.0/category/3/21',
            'http://www.passiontimes.hk/4.0/category/3/24'
        }
        pt_spider = SpiderPt('PtSpider', pt_seed,
                             {r'http://www\.passiontimes\.hk/article/' + util.get_day_string('-', 'american',
                                                                                             offset=offset) + '.*'},
                             THREAD_NUM=10)
        pt_spider.OFFSET = offset
        pt_spider.BATCH_NUMBER = util.get_day_stamp() + 10001
        return pt_spider


if __name__ == '__main__':
    SpiderPt.PUT_IN_STORAGE = False
    SpiderPt.start_crawling()
