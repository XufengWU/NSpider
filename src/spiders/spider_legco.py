# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import json
import requests
from pyquery import PyQuery as pq
import time


complete_pattern = re.compile(ur'http://.+')
date_pattern = re.compile(ur'(\d{4}/\d\d/\d\d \d+:\d+ AM|\d{4}/\d\d/\d\d \d+:\d+ PM)')
cat_pattern_in_url = re.compile(ur'(?<=home/).+?(?=/)')
entry_id_pattern = re.compile(ur'(?<=-).+')
url_id_pattern = re.compile(ur'(?<=MeetingID=).+')
prefix = 'http://webcast.legco.gov.hk'


class SpiderLegco(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = prefix + u
        else:
            u = ''
        return u

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = util.get_time_string_from_selectors(doc, {'.PlaylistRow td'}, date_patterns={date_pattern})
                t_stamp = util.get_timestamp_from_string(t, '%Y/%m/%d %I:%M %p')
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def task_filter(self, doc, url, doc_url):
        return self.page_filter(doc, url)

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'.PlaylistRow kanhanpass'})
        t = util.get_time_string_from_selectors(doc, {'.PlaylistRow td'}, date_patterns={date_pattern})
        t_stamp = util.get_timestamp_from_string(t, '%Y/%m/%d %I:%M %p') + int(time.localtime().tm_sec)
        category = doc('#topMenu a.on').text()
        author = ''
        c_id = re.findall(url_id_pattern, task.url)[0]
        r = requests.get('http://webcast.legco.gov.hk/Public_uat_embedded/Service1.asmx/GetTimeMarker?meetingID=' +
                         c_id +
                         '&lang=tc')
        j_obj = json.loads(r.text)
        content = ''
        for agenda in j_obj['TimeMarkerItems']:
            a_time = agenda['AgendaTime']
            a_item = agenda['AgendaItem']
            content = content + a_time + u' - ' + a_item + u'\n'

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'LegislativeCouncil'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        legco_seed = {'http://webcast.legco.gov.hk/public/zh-hk/SearchResult'}
        r = requests.get('http://webcast.legco.gov.hk/public/zh-hk/SearchResult')
        headers = r.headers
        headers['Referer'] = 'http://webcast.legco.gov.hk/public/zh-hk/SearchResult'
        _page = 1
        while True:
            r = requests.get('http://webcast.legco.gov.hk/public/zh-hk/SearchResult?page=' + str(_page), headers=headers)
            d = pq(r.text)
            t = util.get_time_string_from_selectors(d, {'tr.PlaylistRow td'}, date_patterns={date_pattern})
            t_stamp = util.get_timestamp_from_string(t, '%Y/%m/%d %I:%M %p')
            if t_stamp >= util.get_day_stamp(offset):
                _page += 1
                for entry in d('tr.PlaylistRow').items():
                    if re.findall(entry_id_pattern, entry.attr('id')):
                        c_id = re.findall(entry_id_pattern, entry.attr('id'))[0]
                        legco_seed.add('http://webcast.legco.gov.hk/public/zh-hk/SearchResult?MeetingID=' + c_id)
            else:
                break
        spider_legco = SpiderLegco('SpiderLegco',
                                   legco_seed,
                                   {ur'http://webcast\.legco\.gov\.hk/public/zh-hk/SearchResult\?MeetingID=.+'},
                                   THREAD_NUM=5)
        spider_legco.OFFSET = offset
        spider_legco.BATCH_NUMBER = util.get_day_stamp() + 10300
        return spider_legco


if __name__ == '__main__':

    SpiderLegco.PUT_IN_STORAGE = False
    SpiderLegco.start_crawling()
