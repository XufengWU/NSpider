# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import requests
import json
from pyquery import PyQuery as pq

prefix = u'http://news.mingpao.com'
media_prefix = 'http://fs.mingpao.com/'
complete_pattern = re.compile(ur'(http|https)://.+')
news_list_data_pattern = re.compile(r'(?<=\':).*(?=};)')
no_use_txt_pattern = re.compile(ur'((其他報道：|■明報報料熱線﹕).+\n)')


class SpiderMingPao(common_news_spider.CommonNewsSpider):
    def add_new_urls(self, task, response):
        pass

    def get_doc(self, response):
        try:
            return json.loads(response.text)
        except ValueError:
            return None

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        if doc:
            title = doc['TITLE']
            t = doc['PUBDATE']
            t_stamp = util.get_timestamp_from_string(t) + 8 * 3600
            category = doc['SUMMARY']['section1']['SECTIONNAME']
            author = doc['AUTHOR']
            pq_obj = pq(doc['DESCRIPTION'])
            content = ''
            for p in pq_obj('p').items():
                content += p.text() + '\n'
            item.raw = response.text
            item.title = title
            item.t = t
            item.t_stamp = t_stamp
            item.fetched_at = task.fetched_at
            item.category = category
            item.author = author
            item.content = re.sub(no_use_txt_pattern, u'', content)
            item.url = task.url
            item.source = 'MingPao'
            item.task_no = self.BATCH_NUMBER
            if doc['media:group'] and doc['media:group'] != []:
                for m in doc['media:group']:
                    m_title = m['media:title']
                    for m_c in m['media:content']:
                        m_c = m_c['ATTRIBUTES']
                        if m_c['MEDIUM'] == 'image' and m_c['SIZETYPE'] == 'SF':
                            m_url = media_prefix + m_c['URL']
                            if m_url:
                                media = self.NewsItem.MediaItem(media_url=m_url, type='image', description=m_title,
                                                                created_at=item.fetched_at)
                                item.media_list.append(media)
                        elif m_c['MEDIUM'] == 'video':
                            print m_c
                            m_url = m_c['URL']
                            if m_url:
                                media = self.NewsItem.MediaItem(media_url=m_url, type='youtube', description=m_title,
                                                                created_at=item.fetched_at)
                                item.media_list.append(media)

    @classmethod
    def get_auto_configured_spider(cls, offset=0, **kwargs):
        day_str = util.get_day_string(offset=offset)
        issue_dict_url = 'http://news.mingpao.com/dat/pns/issuelist.js?819181'
        r = requests.get(issue_dict_url)
        json_obj = json.loads(r.text)
        if '1 ' + day_str in json_obj['PNS_WEB_TC']:
            issue_id = json_obj['PNS_WEB_TC']['1 ' + day_str]['E']
        else:
            print 'KEY ERROR: ' + json_obj['PNS_WEB_TC']['1 ' + day_str]
            return
        news_list_url = 'http://news.mingpao.com/dat/pns/pns_web_tc/feed1/' + day_str + issue_id + '/content.js'
        mingpao_seed = set()
        r = requests.get(news_list_url)
        if re.findall(r'feed_module_2', r.text):
            news_list_data = news_list_data_pattern.findall(r.text)[0]
            json_obj = json.loads(news_list_data)
            for it in json_obj['rss']['channel']['item']:
                mingpao_seed.add(
                    'http://news.mingpao.com/dat/pns/pns_web_tc/article1/' + day_str + issue_id.lower() + '/todaycontent_' + str(
                        it['ATTRIBUTES']['NODEID']) + '.js')
        mingpao_reg = {ur'http://news\.mingpao\.com/dat/pns/.*' + day_str + '.+'}
        spider_mingpao = SpiderMingPao('SpiderMingPao', mingpao_seed, mingpao_reg, THREAD_NUM=10)
        spider_mingpao.OFFSET = offset
        spider_mingpao.BATCH_NUMBER = util.get_day_stamp(offset) + 10570
        return spider_mingpao


if __name__ == '__main__':
    SpiderMingPao.PUT_IN_STORAGE = False
    SpiderMingPao.start_crawling()
