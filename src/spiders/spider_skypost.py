# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import urllib2
import time


page_prefix = ur'http://skypost.ulifestyle.com.hk'
complete_pattern = re.compile(ur'http://.*')
cat_pattern = re.compile(ur'(?<=hk/).*(?=/\d{8}/.+)')


class SpiderSkyPost(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = ''
        if link.attr('href'):
            u = link.attr('href')
            if not complete_pattern.match(u):
                u = page_prefix + u
        return u

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, ur'\s*\|.*')
        t = util.get_time_string_from_selectors(doc, {'div.PolDTextBox_Date', 'div.MainNews_Date'})
        t = t[-4:] + t[3:5] + t[:2]
        t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_hour*3600 + time.localtime().tm_min*60 + time.localtime().tm_sec
        category = ''
        if cat_pattern.findall(task.url):
            category = cat_pattern.findall(task.url)[0]
            category = urllib2.unquote(category)
        author = ''
        content = util.get_paragraphs_from_selector(doc, 'div.PolDTextBox div')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, 'div.MainNews_Text div')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'SkyPost'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.PolDetailBox img').items():
            if img.attr('src') != '':
                media_u = img.attr('src')
                des = ''
                if img.parent().siblings('.PolDCaption'):
                    des = img.parent().siblings('.PolDCaption').text()
                elif img.parents('.NewsDPicBox02'):
                    des = img.parents('.NewsDPicBox02').text()
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
            _comments = util.get_filtered_facebook_comments_data('335749279848103',
                                                                 doc('div.fb-comments').attr('data-href'), task.url)
            if _comments:
                for _comment in _comments:
                    item.media_list.append(
                        self.NewsItem.MediaItem(media_url=_comment['json_string'], type='comments',
                                                description='comments', created_at=item.fetched_at)
                    )

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        archive_page_url = 'http://skypost.ulifestyle.com.hk/archive/' + util.get_day_string(offset=offset) + '/'
        skypost_seed = {archive_page_url, 'http://skypost.ulifestyle.com.hk/'}
        skypost_reg = {ur'http://skypost\.ulifestyle\.com\.hk/.*/' +
                       util.get_day_string(offset=offset) +
                       ur'/.*?/.+'}
        spider_skypost = SpiderSkyPost('SpiderSkyPost', skypost_seed, skypost_reg, THREAD_NUM=10)
        spider_skypost.OFFSET = offset
        spider_skypost.BATCH_NUMBER = util.get_day_stamp() + 10140
        return spider_skypost


if __name__ == '__main__':

    SpiderSkyPost.PUT_IN_STORAGE = False
    SpiderSkyPost.start_crawling()

