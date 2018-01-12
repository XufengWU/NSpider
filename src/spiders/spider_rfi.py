# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import urllib


complete_pattern = re.compile(ur'http://.+')
cat_pattern_in_url = re.compile(ur'(?<=fr/).+?(?=/)')
prefix = 'http://cn.rfi.fr'


class SpiderRFI(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = prefix + u
        else:
            u = ''
        return u

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'header h1'})
        if title == '':
            title = doc('.edition-title').text()
        t = doc('meta[property="article:published_time"]').attr('content')
        t_stamp = util.get_timestamp_from_string(t) + 2*3600
        category = doc('header .meta .tag:last-child').text()
        if category == '':
            if cat_pattern_in_url.findall(task.url):
                category = cat_pattern_in_url.findall(task.url)[0]
                category = urllib.unquote(category)
        author = doc('span[itemprop="name"]').text()
        content = util.get_paragraphs_from_selector(doc, '.intro p') + util.get_paragraphs_from_selector(doc, 'div[itemprop="articleBody"] p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'RFI'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.media img[itemprop="image"], .page-container .viewport img').items():
            if img.attr('src') != '':
                media_u = img.attr('src')
                des = ''
                if img.siblings('small'):
                    des = img.siblings('small').text()
                elif img.attr('alt'):
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
        rfi_seed = {'http://cn.rfi.fr/%E6%B8%AF%E6%BE%B3%E5%8F%B0/all/'}
        day_str = util.get_day_string(offset=offset)
        spider_rfi = SpiderRFI('SpiderRFI',
                               rfi_seed,
                               {ur'http://cn.rfi.fr/.*' + day_str + '.+'},
                               THREAD_NUM=10)
        spider_rfi.BATCH_NUMBER = util.get_day_stamp() + 10510
        spider_rfi.OFFSET = offset
        return spider_rfi


if __name__ == '__main__':

    SpiderRFI.PUT_IN_STORAGE = False
    SpiderRFI.start_crawling()
