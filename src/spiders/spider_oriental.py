# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import requests
import threading


prefix = u'http://orientaldaily.on.cc'
complete_pattern = re.compile(ur'(http|https)://.+')
today_date_pattern = re.compile(util.get_day_string())
charset_pattern = re.compile(ur'(?<=charset=).+?(?=")')
cat_pattern = re.compile(ur'(?<=cnt/).+?(?=/)')
cat_pattern_2 = re.compile(ur'(?<=\d\d\d\d/).+?(?=/)')
title_pattern = re.compile(r'(?<=<!--title-->).*?(?=<!--/title-->)')
cat_dict = {'new': u'要聞港聞',
            'fin': u'財經',
            'spt': u'體育',
            'ent': u'娛樂',
            'fea': u'副刊',
            'com': u'投訴',
            'fnd': u'慈善基金',
            'new_f': u'評論',
            'hrs': u'馬經'}


class SpiderOriental(common_news_spider.CommonNewsSpider):

    charset_found = ''
    charset_lock = threading.RLock()

    def send_request(self, task):
        r = requests.get(task.url, timeout=self.RESPONSE_TIMEOUT_VALUE)
        with self.charset_lock:
            if self.charset_found == '':
                if charset_pattern.findall(r.text):
                    self.charset_found = charset_pattern.findall(r.text)[0]
                else:
                    self.charset_found = 'big5'
        r.encoding = self.charset_found
        task.fetched_at = util.get_now()
        return r

    def get_url_of_link(self, link, doc, doc_url):
        u = ''
        if link.attr('href'):
            u = link.attr('href')
        if u is not '' and not complete_pattern.match(u):
            u = prefix + u
        return u

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1:not(.articleDate)'})
        if title == '':
            title = doc('.bigtitlelink').text()
        if title == '':
            title = doc('font[size="5"]').text()
        t = util.get_day_string(offset=self.OFFSET)
        t_stamp = util.get_day_stamp(self.OFFSET)
        if t_stamp >= util.get_day_stamp(0):
            t_stamp = util.get_now()
        category = ''
        if cat_pattern.findall(task.url):
            cat_word = cat_pattern.findall(task.url)[0]
            category = doc('.' + cat_word).text()
        if category == '':
            if re.findall(cat_pattern_2, task.url):
                cat = re.findall(cat_pattern_2, task.url)[0]
                if cat in cat_dict:
                    category = cat_dict[cat]
        author = ''
        content = util.get_paragraphs_from_selector(doc, '.leadin p') + util.get_paragraphs_from_selector(doc, '#contentCTN-right p,h3')
        if doc('.summaryPara'):
            content = util.get_paragraphs_from_selector(doc, '.summaryPara') + util.get_paragraphs_from_selector(doc, '.newsText p')
        if content == '':
            content = doc('tr p').text()
        if content == '':
            if doc('tr'):
                for tr in doc('tr').items():
                    for thd in tr('th,td').items():
                        content += u'{:<20}'.format(thd.text())
                    content += u'\n'

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'OrientalDaily'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.photo img').items():
            if img.attr('src') != '':
                media_u = prefix + img.attr('src')
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
        oriental_seed = {'http://orientaldaily.on.cc/cnt/sitemap/' +
                         util.get_day_string(offset=offset) +
                         '/index.html'}
        oriental_reg = {ur'http://orientaldaily\.on\.cc/cnt/.+' +
                        util.get_day_string(offset=offset) +
                        r'/[\d_]+.html',
                        ur'http://orientaldaily\.on\.cc/archive/' +
                        util.get_day_string(offset=offset) +
                        '.+\.html'}
        spider_oriental = SpiderOriental('SpiderOriental', oriental_seed, oriental_reg, THREAD_NUM=15)
        spider_oriental.OFFSET = offset
        spider_oriental.BATCH_NUMBER = util.get_day_stamp(offset) + 10310
        return spider_oriental


if __name__ == '__main__':

    for i in range(31, 32):
        SpiderOriental.PUT_IN_STORAGE = False
        SpiderOriental.DEFAULT_PUT_IN_FILE = False
        SpiderOriental.start_crawling(offset=i)
