# -*- coding:utf-8 -*-
import common_news_spider
import util
import threading
import time
import re
import requests


class SpiderHK01(common_news_spider.CommonNewsSpider):

    _doc = None
    _doc_wanted = False
    _doc_lock = threading.Lock()

    def get_url_of_link(self, link, doc, doc_url):
        href = link.attr('href')
        if href == '#':
            href = link.attr('data-href')
        return href

    # filter the page not only from url, but also its content
    def page_filter(self, doc, url):
        t_stamp = util.get_day_stamp(self.OFFSET)
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if doc('meta[name=artpdate]').attr('content'):
                    if int(time.mktime(time.strptime(doc('meta[name=artpdate]').attr('content'),
                                                     "%Y-%m-%d %H:%M:%S"))) >= t_stamp:
                        wanted = True
        return wanted

    # filter of tasks to do     **Note that 'doc' is not the response of 'url'
    def task_filter(self, doc, url, doc_url):
        t_stamp = util.get_day_stamp(self.OFFSET)
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if doc('meta[name=artpdate]').attr('content') is not None:
                    if int(time.mktime(time.strptime(doc('meta[name=artpdate]').attr('content'),
                                                     "%Y-%m-%d %H:%M:%S"))) >= t_stamp:
                        wanted = True
                else:
                    wanted = True
        return wanted

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        item.raw = doc.text()
        item.title = util.get_filtered_title(doc, {'.article_tit h1'}, ur'\s*｜.*')
        if item.title == '':
            item.title = util.get_filtered_title(doc, {'title'}, ur'\s*｜.*')
        item.t = doc('meta[name=artpdate]').attr('content')
        item.t_stamp = int(time.mktime(time.strptime(item.t, "%Y-%m-%d %H:%M:%S")))
        item.fetched_at = task.fetched_at
        item.category = doc('meta[name=catname]').attr('content')
        item.author = doc('meta[name=author]').attr('content')
        content = util.get_paragraphs_from_selector(doc, 'div.article_content__module p')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, 'li.article_summary_pt')
        item.content = content
        item.url = task.url
        item.source = 'HK01'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.article__body__content img').items():
            if img.attr('src') != '' and not img.parents('.related_article'):
                media_u = img.attr('src')
                if media_u != '//cdn.hk01.com/media/dummy/default_image.png':
                    des = ''
                    if img.attr('alt'):
                        des = img.attr('alt')
                    media = self.NewsItem.MediaItem(media_url=media_u, type='image', description=des,
                                                    created_at=item.fetched_at)
                    item.media_list.append(media)
        for img in doc('.article__body__content object[data-gallery-image="true"]').items():
            if img.attr('data'):
                media_u = img.attr('data')
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
        if util.within_active_interval(6, 1200):
            _comments = util.get_filtered_facebook_comments_data('1651866545051541', doc('div.fb-comments').attr('data-href'), task.url)
            if _comments:
                for _comment in _comments:
                    item.media_list.append(
                        self.NewsItem.MediaItem(media_url=_comment['json_string'], type='comments', description='comments', created_at=item.fetched_at)
                )
        '''
        # get comments
        comments = requests.get(
            "https://www.facebook.com/plugins/feedback.php?api_key&channel_url=http%3A%2F%2Fstaticxx.facebook.com%2Fconnect%2Fxd_arbiter.php%3Fversion%3D42%23cb%3Df2078a41baf3aa%26domain%3Dwww.hk01.com%26origin%3Dhttp%253A%252F%252Fwww.hk01.com%252Ff13d240195995b%26relation%3Dparent.parent"
            + "&href=" + task + "&locale=zh_HK&numposts=" + str(100) + "&sdk=joey&version=v2.5&width=100%25")
        c_dict = json.loads(re.compile(ur'(?<="comments":).*?\}(?=,"meta")').findall(comments.text)[0])
        id_map = c_dict['idMap']
        comment_ids = c_dict['commentIDs']
        print "Comments: "
        for cid in comment_ids:
            cid = cid.encode('utf-8')
            uid = id_map[cid]['authorID']
            print "Author name: " + id_map[uid]['name']
            print "Comment content: " + id_map[cid]['body']['text']
        '''

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        hkspider = SpiderHK01('HK01Spider', {'http://www.hk01.com/'}, {ur'(http|https)://www.hk01.com/.*/\d{5}/.*'},
                              THREAD_NUM=10)
        hkspider.BATCH_NUMBER = util.get_day_stamp() + 10002
        hkspider.OFFSET = offset
        return hkspider


if __name__ == '__main__':
    SpiderHK01.PUT_IN_STORAGE = False
    SpiderHK01.ADD_MEDIA = True
    # SpiderHK01.DEFAULT_PUT_IN_FILE = True
    # _urls = set()
    # for i in range(10):
    #     _urls.add('https://www.hk01.com/api/get_articles/22/' + str(i) + '/90?TEMPLATES=blog_listing')
    SpiderHK01.start_crawling()
