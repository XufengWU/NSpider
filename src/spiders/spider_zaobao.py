# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import threading


complete_pattern = re.compile(ur'http://.+')
news_prefix = 'http://www.zaobao.com'
news_id_pattern = re.compile(util.get_day_string() + ur'-\d+')


class SpiderZaobao(common_news_spider.CommonNewsSpider):

    ids = set()
    id_lock = threading.RLock()

    def get_url_of_link(self, link, doc, doc_url):

        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = news_prefix + u
        else:
            u = ''
        return u

    def normal_item_check(self, item, task, response):
        doc_url = task.url
        if item.id != '':
            with self.id_lock:
                if item.id in self.ids:
                    self.ids.add(item.id)
                    self.logger_con.warning('DUPLICATED NEWS: ' + doc_url)
                    self.logger_file.warning('DUPLICATED NEWS: ' + doc_url)
                    return False
                self.ids.add(item.id)
        if item.t == '':
            self.logger_con.warning('NO TIME: ' + doc_url)
            self.logger_file.warning('NO TIME: ' + doc_url)
            return False
        if item.title == '':
            self.logger_con.warning('NO TITLE: ' + doc_url)
            self.logger_file.warning('NO TITLE: ' + doc_url)
            return False
        if item.category == '':
            self.logger_con.warning('NO CAT: ' + doc_url)
            self.logger_file.warning('NO CAT: ' + doc_url)
        if item.content == '':
            self.logger_con.warning('NO CONTENT: ' + doc_url)
            self.logger_file.warning('NO CONTENT: ' + doc_url)
            return False
        return True

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1'})
        t = doc('span.datestamp').text()
        t_stamp = util.get_timestamp_from_string(t)
        category = ''
        category = doc('#breadcrumbs a:last-child').text()
        author = ''
        author = doc('.contributor a').text()
        content = util.get_paragraphs_from_selector(doc, '.article-content-container p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'ZaoBao'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.loadme picture').items():
            if img('source') and img('source').attr('data-srcset'):
                media_u = img('source:first-child').attr('data-srcset')
                des = ''
                if img.attr('title'):
                    des = img.attr('title')
                elif img('img') and img('img').attr('title'):
                    des = img('img').attr('title')
                media = self.NewsItem.MediaItem(media_url=media_u, type='image', description=des,
                                                created_at=item.fetched_at)
                item.media_list.append(media)
        # for a in doc('iframe').items():
        #     if a.attr('src') and re.match(r'.*youtube\.com.+', a.attr('src')):
        #         media_u = a.attr('src')
        #         if re.match(r'//.+', media_u):
        #             media_u = 'http:' + media_u
        #         media = self.NewsItem.MediaItem(media_url=media_u, type='youtube', description='youtube',
        #                                         created_at=item.fetched_at)
        #         item.media_list.append(media)
        if news_id_pattern.findall(task.url):
            item.id = news_id_pattern.findall(task.url)[0]
        else:
            item.id = ''

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        zaobao_seed = {'http://www.zaobao.com/', 'http://www.zaobao.com/realtime#CN/'}
        spider_zaobao = SpiderZaobao('SpiderZaobao',
                                     zaobao_seed,
                                     {ur'http://.+' +
                                      util.get_day_string(offset=offset) +
                                      '-.+'},
                                     THREAD_NUM=5)
        spider_zaobao.OFFSET = offset
        spider_zaobao.BATCH_NUMBER = util.get_day_stamp() + 10330
        return spider_zaobao

if __name__ == '__main__':
    SpiderZaobao.PUT_IN_STORAGE = False
    SpiderZaobao.start_crawling()
