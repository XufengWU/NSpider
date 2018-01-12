# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time


page_prefix = ur'http://news.rthk.hk'
complete_pattern = re.compile(ur'http://news\.rthk\.hk.*')
cat_pattern = re.compile(ur'(?<=class="pathway">).*?(?=<)')


class SpiderRTHK(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = ''
        if link.attr('href'):
            u = link.attr('href')
            if not complete_pattern.match(u):
                u = page_prefix + u
        return u

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, ur' - RTHK')
        t = util.get_time_string_from_selectors(doc, {'div.createddate'})
        t_stamp = util.get_timestamp_from_string(t, '%Y-%m-%d HKT %H:%M') + time.localtime().tm_sec
        category = ''
        if cat_pattern.findall(doc('script').text()):
            category = cat_pattern.findall(doc('script').text())[-1]
        author = ''
        content = util.get_paragraphs_from_selector(doc, 'div.itemFullText')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'RTHK'
        item.task_no = self.BATCH_NUMBER
        for img in doc('img.imgPhotoAfterLoad').items():
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
        current_day_string = util.get_day_string(offset=offset)
        day_string = 'archive_year=' + current_day_string[0:4] + '&archive_month=' + current_day_string[4:6] + '&archive_day=' + current_day_string[6:8]
        instant_news_page_url = 'http://news.rthk.hk/rthk/ch/news-archive.htm?' + day_string + '&archive_cat=all'
        rthk_seed = {instant_news_page_url}
        rthk_reg = {ur'http://news\.rthk\.hk/rthk/ch/component/.*' +
                    util.get_day_string(offset=offset) +
                    '.*'}
        spider_rthk = SpiderRTHK('SpiderRTHK', rthk_seed, rthk_reg, THREAD_NUM=5)
        spider_rthk.BATCH_NUMBER = util.get_day_stamp() + 10130
        spider_rthk.OFFSET = offset
        return spider_rthk


if __name__ == '__main__':

    SpiderRTHK.PUT_IN_STORAGE = False
    SpiderRTHK.start_crawling()
