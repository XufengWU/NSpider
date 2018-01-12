# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time
import requests


incomplete_pattern = re.compile(ur'/\d{4}/\d\d/\d\d/.+')
cat_pattern = re.compile(ur'(?<=> ).+?(?= >)')


class SpiderWenWei(common_news_spider.CommonNewsSpider):

    def send_request(self, task):
        r = requests.get(task.url, timeout=self.RESPONSE_TIMEOUT_VALUE)
        r.encoding = 'big5hkscs'
        task.fetched_at = util.get_now()
        return r

    def get_url_of_link(self, link, doc, doc_url):

        u = link.attr('href')
        news_prefix = 'http://news.wenweipo.com'
        if u is not None:
            if incomplete_pattern.match(u):
                u = news_prefix + u
        else:
            u = ''
        return u

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, ur'\s*-\s*(香港文匯報|香港文匯網)')
        t = doc('span.date').text()
        t_stamp = util.get_timestamp_from_string(t)
        current_date = str(time.localtime().tm_year) + ('%02d' % time.localtime().tm_mon) + (
            '%02d' % time.localtime().tm_mday)
        if t_stamp >= int(time.mktime(time.strptime(current_date, "%Y%m%d"))):
            t_stamp = util.get_now()
        category = ''
        if re.findall(cat_pattern, doc('span.current').text().encode('utf-8')):
            category = re.findall(cat_pattern, doc('span.current').text().encode('utf-8'))[-1]
        author = ''
        content = util.get_paragraphs_from_selector(doc, 'div[id=main-content] p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'WenWei'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.imgtxt img').items():
            if img.attr('src') != '':
                media_u = img.attr('src')
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
        wenwei_seed = {'http://www.wenweipo.com/', 'http://news.wenweipo.com/list_srh.php?date='+util.get_day_string(offset=offset)}
        spider_wenwei = SpiderWenWei('SpiderWenWei',
                                     wenwei_seed,
                                     {ur'http://(news|paper)\.wenweipo\.com/' +
                                      util.get_day_string(interval_str='/', offset=offset) +
                                      '/.+'},
                                     THREAD_NUM=10)
        spider_wenwei.OFFSET = offset
        spider_wenwei.BATCH_NUMBER = util.get_day_stamp() + 10090
        return spider_wenwei


if __name__ == '__main__':
    SpiderWenWei.PUT_IN_STORAGE = False
    SpiderWenWei.start_crawling()
