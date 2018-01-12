# -*- coding:utf-8 -*-
import common_news_spider
import util
import json
import re
import time


tk_pattern = re.compile(ur'http://\w+\.takungpao\.com/.*')
tk_hk_pattern = re.compile(ur'http://www\.takungpao\.com\.hk/.*')
incomplete_t_pattern = re.compile(ur'/' + str(time.localtime().tm_year) + '-' + ('%02d' % time.localtime().tm_mon) + '/')
complete_t_pattern = re.compile(ur'/' + str(time.localtime().tm_year) + '/' + ('%02d' % time.localtime().tm_mon) + ('%02d' % time.localtime().tm_mday) + '/')
t_p = re.compile(ur'\d{4}.*:\d\d')
pic_list_pattern = re.compile(ur'(?<=picList =).*?(?=;)')


class SpiderTaKungPao(common_news_spider.CommonNewsSpider):

    def __init__(self, name='NewSpider', seed=None, reg=None, MAX_DEPTH=1, THREAD_NUM=1, cats=None, cats_hk=None):
        common_news_spider.CommonNewsSpider.__init__(self, name, seed, reg, MAX_DEPTH, THREAD_NUM)
        self._cats = cats
        self._cats_hk = cats_hk

    def page_filter(self, doc, url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if complete_t_pattern.findall(url):
                    return True
                elif incomplete_t_pattern.findall(url):
                    t = ''
                    if doc('ul.content_info span:first-child'):
                        t = doc('ul.content_info span:first-child').text()
                    elif doc('h2.tkp_con_author span:first-child'):
                        t = doc('h2.tkp_con_author span:first-child').text()
                    elif doc('div.fl_dib'):
                        if re.findall(t_p, doc('div.fl_dib').text()):
                            t = re.findall(t_p, doc('div.fl_dib').text())[0]
                        else:
                            return False
                    if t == '':
                        return False
                    t_stamp = util.get_timestamp_from_string(t, '%Y-%m-%d %H:%M:%S')
                    if t_stamp >= util.get_day_stamp(self.OFFSET):
                        wanted = True
        return wanted

    def task_filter(self, doc, url, doc_url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if not reg_pattern.match(doc_url):
                    return True
                if complete_t_pattern.findall(url):
                    return True
                elif incomplete_t_pattern.findall(url):
                    t = ''
                    if doc('ul.content_info span:first-child'):
                        t = doc('ul.content_info span:first-child').text()
                    elif doc('h2.tkp_con_author span:first-child'):
                        t = doc('h2.tkp_con_author span:first-child').text()
                    elif doc('div.fl_dib'):
                        if re.findall(t_p, doc('div.fl_dib').text()):
                            t = re.findall(t_p, doc('div.fl_dib').text())[0]
                        else:
                            return False
                    if t == '':
                        return False
                    t_stamp = util.get_timestamp_from_string(t, '%Y-%m-%d %H:%M:%S')
                    if t_stamp >= util.get_day_stamp(self.OFFSET):
                        wanted = True
        return wanted

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        t = ''
        title = ''
        t_stamp = 0
        category = ''
        content = ''
        author = ''
        if tk_pattern.match(task.url):
            title = util.get_filtered_title(doc, {'title'}, ur'_.*')
            if doc('ul.content_info span:first-child'):
                t = doc('ul.content_info span:first-child').text()
            elif doc('div.fl_dib'):
                if re.findall(t_p, doc('div.fl_dib').text()):
                    t = re.findall(t_p, doc('div.fl_dib').text())[0]
            t_stamp = util.get_timestamp_from_string(t)  # int(time.mktime(time.strptime(t, '%Y-%m-%d %H:%M:%S')))
            for cat_k, cat_v in self._cats.iteritems():
                if task.url.find(cat_k) is not -1:
                    category = cat_v
                    break
            content = util.get_paragraphs_from_selector(doc, 'p:not(.adCon_tj_tle)')
            if content == '':
                json_str = re.sub(u'var datas=', u'', doc('#json_data').text())
                json_str = re.sub(u"'", u'"', json_str)
                j_ob = json.loads(json_str)
                content = j_ob['imgs'][0]['info_txt']
        elif tk_hk_pattern.match(task.url):
            title = doc('title').text()
            t = doc('h2.tkp_con_author span:first-child').text()
            t_stamp = util.get_timestamp_from_string(t, '%Y-%m-%d %H:%M:%S')
            if doc('div.article_path a:last-child'):
                category = doc('div.article_path a:last-child').text()
            elif doc('#picTitle'):
                for cat_k, cat_v in self._cats_hk.iteritems():
                    if task.url.find(cat_k) is not -1:
                        category = cat_v
                        break
            if doc('p'):
                content = util.get_paragraphs_from_selector(doc, 'p')
            elif doc('div.tkp_content'):
                content = util.get_paragraphs_from_selector(doc, 'div.tkp_content p, div.tkp_content div')
            elif doc('#picTitle'):
                scripts = doc('script').text()
                if pic_list_pattern.findall(scripts):
                    pic_titles = pic_list_pattern.findall(scripts)[0]
                    j_pick_titles = json.loads(pic_titles)
                    content = j_pick_titles[0]['title']

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'TaKungPao'
        item.task_no = self.BATCH_NUMBER
        for img in doc('p img, center img').items():
            if img.attr('src') != '':
                media_u = img.attr('src')
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

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        tk_seed = {'http://www.takungpao.com/'}
        tk_seed.add('http://www.takungpao.com.hk/')
        util.add_hrefs('http://www.takungpao.com/', {'.navList li a'}, tk_seed)
        util.add_hrefs('http://www.takungpao.com.hk/', {'.nav_list li a'}, tk_seed)
        cats = dict()
        cats_hk = dict()
        util.update_cat_dict_from_selectors('http://www.takungpao.com/', selectors={'div.navList a'}, cats=cats)
        util.update_cat_dict_from_selectors('http://www.takungpao.com/corp/sitemap.html', selectors={'.clearfix a'}, cats=cats)
        util.update_cat_dict_from_selectors('http://www.takungpao.com.hk/', selectors={'ul.nav_list a'}, cats=cats_hk)
        day_str = util.get_day_string(offset=offset)
        day_str = day_str[0:4] + '/' + day_str[4:]
        tk_reg = {ur'http://\w+\.takungpao\.com/.*/' +
                  day_str[0:4] + '-' + day_str[5:7] +
                  '/\d+.*',
                  ur'http://\w+\.takungpao\.com\.hk/.*/' +
                  day_str +
                  '/\d+.*'}
        spider_takung = SpiderTaKungPao('SpiderTaKung', tk_seed, tk_reg, THREAD_NUM=10, MAX_DEPTH=5, cats=cats, cats_hk=cats_hk)
        spider_takung.OFFSET = offset
        spider_takung.BATCH_NUMBER = util.get_day_stamp(offset=0) + 10100
        return spider_takung


if __name__ == '__main__':

    SpiderTaKungPao.PUT_IN_STORAGE = False
    SpiderTaKungPao.start_crawling()


