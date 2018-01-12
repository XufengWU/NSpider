# -*- coding:utf-8 -*-
import common_news_spider
import util
import re


complete_pattern = re.compile(ur'http://.+')
prefix = 'http://www.scmp.com'


class SpiderSCMP(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = prefix + u
        else:
            u = ''
        u = re.sub(r'#comments', '', u)
        return u

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = doc('div[itemprop="dateCreated"]').attr('datetime')
                t_stamp = util.get_timestamp_from_string(t) + 8*3600
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if not reg_pattern.match(doc_url):
                    return True
                t = doc('div[itemprop="dateCreated"]').attr('datetime')
                t_stamp = util.get_timestamp_from_string(t) + 8*3600
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1'})
        t = doc('div[itemprop="dateCreated"]').attr('datetime')
        t_stamp = util.get_timestamp_from_string(t) + 8*3600
        category = doc('.pane-content .lineage-item:last-child').text()
        author = doc('.scmp-v2-author-name').text()
        content = util.get_paragraphs_from_selector(doc, '.pane-content p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'SCMP'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.scmp-gallery-swiper img').items():
            if img.attr('data-original') != '':
                media_u = img.attr('data-original')
                des = ''
                if img.attr('data-caption'):
                    des = img.attr('data-caption')
                media = self.NewsItem.MediaItem(media_url=media_u, type='image', description=des,
                                                created_at=item.fetched_at)
                item.media_list.append(media)
        for a in doc('iframe').items():
            if a.attr('data-original') and re.match(r'.*youtube\.com.+', a.attr('data-original')):
                media_u = a.attr('data-original')
                des = ''
                if a.children('title'):
                    des = a.children('title').text()
                media = self.NewsItem.MediaItem(media_url=media_u, type='youtube', description=des,
                                                created_at=item.fetched_at)
                item.media_list.append(media)

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        scmp_seed = {'http://www.scmp.com/news/hong-kong'}
        spider_scmp = SpiderSCMP('SpiderSCMP',
                                 scmp_seed,
                                 {ur'http://www\.scmp\.com/news/hong-kong/.*article/\d+/.*'},
                                 THREAD_NUM=10)
        spider_scmp.BATCH_NUMBER = util.get_day_stamp() + 10550
        spider_scmp.OFFSET = offset
        return spider_scmp


if __name__ == '__main__':

    SpiderSCMP.PUT_IN_STORAGE = False
    SpiderSCMP.start_crawling()
