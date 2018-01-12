# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import re
import requests
from pyquery import PyQuery as pq


date_patterns = {re.compile(ur'\d{4}年 *\d+月 *\d+日 *\d\d:\d\d')}
hkcd_hk_prefix = 'http://hk.hkcd.com/'
hkcd_hk_pattern = re.compile(ur'http://hk\.hkcd\.com/.*')
hkcd_prefix = 'http://www.hkcd.com/'
hkcd_pattern = re.compile(ur'http://www\.hkcd\.com/.*')
node_pattern = re.compile(ur'node_.*')
content_pattern = re.compile(ur'content/\d{4}-\d\d/\d\d/.*')
cat_block_pattern = re.compile(ur'case \d+:[\n\t\r]*.*[\n\t\r]*.*?innerText=".*?"')
cat_id_pattern = re.compile(ur'(?<=case )\d+(?=:)')
cat_name_pattern = re.compile(ur'(?<=innerText=").*?(?=")')


class SpiderHKCD(common_news_spider.CommonNewsSpider):

    _hk_cat_dict = None
    _cat_dict = None

    def send_request(self, task):
        r = requests.get(task.url, timeout=self.RESPONSE_TIMEOUT_VALUE)
        r.encoding = 'utf-8'
        task.fetched_at = util.get_now()
        return r

    def get_url_of_link(self, link, doc, doc_url):
        if link.attr('href'):
            u = link.attr('href')
            if not hkcd_pattern.findall(u):
                if hkcd_pattern.findall(doc_url):
                    u = hkcd_prefix + u
                else:
                    u = hkcd_hk_prefix + u
            return u
        return ''

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        titile = ''
        t = ''
        t_stamp = 0
        category = ''
        author = ''
        content = ''

        if hkcd_pattern.match(task.url):
            title = util.get_filtered_title(doc, {'title'}, ur'-香港商报')
            t = util.get_time_string_from_selectors(doc=doc, selectors={'span.ti_l'})
            t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_hour*3600 + time.localtime().tm_min*60 + time.localtime().tm_sec
            if doc('#erLevel').text() in self._cat_dict:
                category = self._cat_dict[doc('#erLevel').text()]
            elif doc('#yiLevel'):
                cat_id = doc('#yiLevel').text()
                cat_higher_block_pattern = re.compile(
                    ur'if.*cat==' + cat_id + ur'.*[\n\t\r]*.*[\n\t\r]*.*?innerText=".*?"')
                block = cat_higher_block_pattern.findall(doc('script').text())[0]
                category = cat_name_pattern.findall(block)[0]
            content = util.get_paragraphs_from_selector(doc=doc, selector='div.content_main p, div.content_main div')
            # author = doc('.author').text()
        else:
            title = doc('title').text()
            t = util.get_time_string_from_selectors(doc=doc, selectors={'div.wenzi'}, date_patterns=date_patterns)
            t_stamp = util.get_timestamp_from_string(t) + int(time.localtime().tm_sec)
            if content_pattern.findall(task.url)[0] in self._hk_cat_dict:
                category = self._hk_cat_dict[content_pattern.findall(task.url)[0]]
            content = util.get_paragraphs_from_selector(doc, 'div.wenzi p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'HKCD'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.content_main img').items():
            if img.attr('src') != '':
                media_u = img.attr('src')
                if not re.match(r'http.+', media_u) and re.findall(r'.*\.com', task.url):
                    media_u = re.findall(r'.*\.com', task.url)[0] + img.attr('src')
                des = ''
                if img.attr('alt'):
                    des = img.attr('alt')
                media = self.NewsItem.MediaItem(media_url=media_u, type='image', description=des,
                                                created_at=item.fetched_at)
                item.media_list.append(media)

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        hkcd_seed = {'http://hk.hkcd.com/node_25195.htm'}
        util.add_hrefs(url='http://hk.hkcd.com/node_30602.htm', selectors={'a'}, seeds=hkcd_seed,
                       seed_patterns={node_pattern}, prefix='http://hk.hkcd.com/')
        hkcd_seed.add('http://www.hkcd.com/')
        hk_cat_dict = _get_hk_cat_dict(hkcd_seed, {content_pattern})
        cat_dict = _get_cat_dict({'http://www.hkcd.com/content/2016-07/18/content_1008717.html'})
        current_day_sting = util.get_day_string(offset=offset)
        day_string = current_day_sting[0:4] + '-' + current_day_sting[4:6] + '/' + current_day_sting[6:8]
        hkcd_reg = {r'http://(www|hk)\.hkcd\.com/content/' + day_string + '/.*'}
        spider_hkcd = SpiderHKCD('SpiderHKCD', hkcd_seed, hkcd_reg, THREAD_NUM=10, MAX_DEPTH=2)
        spider_hkcd._hk_cat_dict = hk_cat_dict
        spider_hkcd._cat_dict = cat_dict
        spider_hkcd.BATCH_NUMBER = util.get_day_stamp() + 10120
        return spider_hkcd


def _get_cat_dict(seeds=None):
    cat_dict = dict()
    for seed in seeds:
        r = util.get_safe_response(seed)
        if r:
            r.encoding = 'utf-8'
            d = pq(r.text)
            scripts = d('script').text()
            for cat_block in cat_block_pattern.findall(scripts):
                cat_id = cat_id_pattern.findall(cat_block)[0]
                cat_name = cat_name_pattern.findall(cat_block)[0]
                cat_dict[cat_id] = cat_name
    return cat_dict


# key : value <=> incomplete page url : category name
def _get_hk_cat_dict(seeds=None, key_patterns=None):
    cat_dict = dict()
    for seed in seeds:
        r = util.get_safe_response(seed)
        if r:
            r.encoding = 'utf-8'
            d = pq(r.text)
            for a in d('a').items():
                if a.attr('href'):
                    for pat in key_patterns:
                        if pat.match(a.attr('href')) and node_pattern.findall(seed):
                            cat_name = d('a[href="' + node_pattern.findall(seed)[0] + '"]:first-child').text()
                            cat_dict[a.attr('href')] = cat_name
    return cat_dict

if __name__ == '__main__':

    SpiderHKCD.PUT_IN_STORAGE = False
    SpiderHKCD.start_crawling()
