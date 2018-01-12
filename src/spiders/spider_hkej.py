# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import re


instant_prefix = ur'http://www2.hkej.com'
daily_prefix = ur'http://www1.hkej.com'
common_prefix = ur'http://www.hkej.com'
complete_pattern = re.compile(ur'(http|https)://.+')
instant_pattern = re.compile(ur'http://www2\.hkej\.com/instantnews/.*article/.+')
instant_incomplete_pattern = re.compile(ur'/instantnews.*')
daily_pattern = re.compile(ur'http://www1\.hkej\.com/.*dailynews/.*article/.+')
daily_incomplete_pattern = re.compile(ur'/dailynews/.*article/.+')
# common_article_pattern = re.compile(ur'http://www.*\.hkej\.com/.*article/.+')
headline_article_pattern = re.compile(ur'http://www.*\.hkej\.com/.*headline/article/.+')
instant_time_pattern = re.compile(ur'今日 \d{2}:\d{2}\s*')
min_sec_pattern = re.compile(ur'\d{2}:\d{2}')
cat_pattern = re.compile(ur'(?<=class="pathway">).*?(?=<)')


class SpiderHKEJ(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = ''
        if link.attr('href'):
            u = link.attr('href')
            if not complete_pattern.match(u):
                if instant_incomplete_pattern.match(u):
                    u = instant_prefix + u
                elif daily_incomplete_pattern.match(u):
                    u = daily_prefix + u
                else:
                    u = common_prefix + u
        return u

    def page_filter(self, doc, url):
        if instant_pattern.match(url):
            if doc('span.date') and instant_time_pattern.findall(doc('span.date').text()):
                return True
        elif daily_pattern.match(url) or headline_article_pattern.match(url):
            if doc('.date'):
                t_stamp = util.get_timestamp_from_selectors(doc, {'.date'})
                if t_stamp >= util.get_month_day_timestamp(offset=self.OFFSET):
                    return True
                return False
            elif doc('#date'):
                t_stamp = util.get_timestamp_from_selectors(doc, {'#date'})
                if t_stamp >= util.get_month_day_timestamp(offset=self.OFFSET):
                    return True
                return False
            return False
        return False

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if instant_pattern.match(url):
                    if doc('span.date'):
                        if instant_time_pattern.findall(doc('span.date').text()):
                            return True
                        return False
                    return True
                elif daily_pattern.match(url) or headline_article_pattern.match(url):
                    if doc('.date'):
                        t_stamp = util.get_timestamp_from_selectors(doc, {'.date'})
                        if t_stamp >= util.get_month_day_timestamp(offset=self.OFFSET):
                            return True
                        return False
                    elif doc('#date'):
                        t_stamp = util.get_timestamp_from_selectors(doc, {'#date'})
                        if t_stamp >= util.get_month_day_timestamp(offset=self.OFFSET):
                            return True
                        return False
                    return True
                return True
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = ''
        t = ''
        t_stamp = 0
        category = ''
        author = ''
        content = ''

        if instant_pattern.match(task.url):
            title = util.get_filtered_title(doc, {'title'}, ur' - 信報網站 hkej.com')
            t = util.get_time_string_from_selectors(doc, {'span.date'})
            time_part = min_sec_pattern.findall(t)[0]
            t_stamp = util.get_timestamp_from_string(time_part) + time.localtime().tm_sec
            category = doc('span.cate').text()
            content = util.get_paragraphs_from_selector(doc, '#article-content p')
        elif daily_pattern.match(task.url) or headline_article_pattern.match(task.url):
            title = util.get_filtered_title(doc, {'title'}, ur' - .+')
            t = util.get_time_string_from_selectors(doc, {'#date'})
            t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_hour*3600 + time.localtime().tm_min*60 + time.localtime().tm_sec
            category = doc('#hkej_navSubMenu_2014 .on').text()
            content = util.get_paragraphs_from_selector(doc, '#article-content p')
            if content == '':
                content = util.get_paragraphs_from_selector(doc, '#article-detail-wrapper')
                content = re.sub(ur'（節錄）(.|\n|\t|\r)*', u'', content, re.M | re.I | re.U)

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'HKEJ'
        item.task_no = self.BATCH_NUMBER
        for img in doc('#article-detail-wrapper p img, #article-detail-wrapper .hkej_detail_thumb_2014 img').items():
            if img.parent('a').attr('href') != '':
                des = ''
                if img.parent('a') and img.parent('a').attr('title'):
                    des = img.parent('a').attr('title')
                media = self.NewsItem.MediaItem(media_url=img.parent('a').attr('href'), type='image', description=des,
                                                created_at=item.fetched_at)
                item.media_list.append(media)
        for a in doc('iframe').items():
            if a.attr('src') and re.match(r'.*youtube\.com.*', a.attr('src')):
                media_u = a.attr('src')
                if re.match(r'//.+', media_u):
                    media_u = 'http:' + media_u
                media = self.NewsItem.MediaItem(media_url=media_u, type='youtube', description='youtube',
                                                created_at=item.fetched_at)
                item.media_list.append(media)

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        hkej_seed = {'http://www2.hkej.com/instantnews', 'http://www.hkej.com/template/landing11/jsp/main.jsp', 'http://www1.hkej.com/dailynews/toc?date='+util.get_day_string('-', offset=offset)}
        # util.add_hrefs('http://www.hkej.com/template/landing11/jsp/main.jsp', {'a'}, hkej_seed, seed_patterns={re.compile(ur'http://www.*hkej\.com/.+')})
        # ** currently the reg of the pages is only for 'instant news'
        hkej_reg = {ur'http://www.*?\.hkej\.com/instantnews.*article/.+', ur'http://www1\.hkej\.com/.*dailynews/.*article/.+'}
        spider_hkej = SpiderHKEJ('SpiderHKEJ', hkej_seed, hkej_reg, THREAD_NUM=10, MAX_DEPTH=1)
        spider_hkej.BATCH_NUMBER = util.get_day_stamp() + 10150
        spider_hkej.OFFSET = offset
        return spider_hkej


if __name__ == '__main__':

    SpiderHKEJ.PUT_IN_STORAGE = False
    SpiderHKEJ.start_crawling()
