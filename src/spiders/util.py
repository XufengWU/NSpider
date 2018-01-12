# -*- coding:utf-8 -*-
import time
import re
import requests
from pyquery import PyQuery as pq
from dateparser import parse
import threading
import logging
import json
import codecs
import urllib

logger_con = logging.getLogger('common_news_spider_console_log')
logger_file = logging.getLogger('common_news_spider_file_log')

# the lock of strptime() method in 'datetime' or 'time' module
# this method can cause error when multi-threading access used
strptime_lock = threading.RLock()

bad_date_pattern = re.compile(r'\d{8}')

# get current timestamp
def get_now():
    return int(time.time())


# safe response
def get_safe_response(url, timeout=30):
    r = None
    try:
        r = requests.get(url, timeout=timeout)
    except Exception, e:
        logger_con.exception(str(e))
        logger_file.exception(str(e))
        logger_con.exception('Error in requesting ' + url)
        logger_file.exception('Error in requesting ' + url)
    finally:
        return r


# get year-mon-day formatted sting list
def get_current_ymd_string_list():
    year = str(time.localtime().tm_year)
    mon = ('%02d' % time.localtime().tm_mon)
    day = ('%02d' % time.localtime().tm_mday)
    return [year, mon, day]


# get filtered title
def get_filtered_title(doc=None, selectors={}, filtered_reg='', sub_reg=''):
    for select in selectors:
        if doc(select):
            title = doc(select).text()
            title = re.sub(filtered_reg, sub_reg, title, re.I | re.U)
            return title
    return ''


# get mon + day + hour (used for task number)
def get_day_stamp(offset=0):
    t_list = list(time.localtime())
    # hour & min & sec = 0
    t_list[3] = t_list[4] = t_list[5] = 0
    day_stamp = int(time.mktime(tuple(t_list)))
    if offset is not 0:
        day_stamp -= offset * (24 * 3600)
    return day_stamp


# get separated paragraphs
def get_paragraphs_from_selector(doc=None, selector=None, stop_string=''):
    paragraphs = ''
    if doc(selector):
        for p in doc(selector).items():
            if p.text() is not '':
                _p_raw = re.sub(ur"<\s*br\s*/*?\s*>", u'\n', unicode(p), re.U | re.M | re.I)
                _p = pq(_p_raw)
                para = _p.text()
                para = re.sub('[\n\r]+', '\n', para)
                paragraphs = paragraphs + para + u'\n'
    return paragraphs


# add seeds from selectors, prefix and seed_patterns
def add_hrefs(url=None, selectors=None, seeds=None, prefix=None, seed_patterns=None):
    r = get_safe_response(url)
    if r and r.status_code == 200:
        try:
            d = pq(r.text)
            for select in selectors:
                if not seed_patterns:
                    for a in d(select).items():
                        if a.attr('href'):
                            if prefix:
                                seeds.add(prefix + a.attr('href'))
                            else:
                                seeds.add(a.attr('href'))
                else:
                    for pat in seed_patterns:
                        for a in d(select).items():
                            if a.attr('href') and pat.match(a.attr('href')):
                                if prefix:
                                    seeds.add(prefix + a.attr('href'))
                                else:
                                    seeds.add(a.attr('href'))
        except Exception, e:
            # possible ParserError
            raise e


# update category dict from selectors
def update_cat_dict_from_selectors(url=None, selectors=None, cats=None):
    for select in selectors:
        r = get_safe_response(url)
        if r and r.status_code == 200:
            try:
                d = pq(r.text)
                for a in d(select).items():
                    if a.attr('href'):
                        cats[a.attr('href')] = a.text()
            except Exception, e:
                # possible ParserError
                raise e


# get the timestamp of someday in this month, offset is the number of days before
def get_month_day_timestamp(offset=0):
    with strptime_lock:
        tm_day = time.localtime().tm_mday
        if tm_day > offset:
            tm_day -= offset
        else:
            tm_day = 1
        current_date = str(time.localtime().tm_year) + ('%02d' % time.localtime().tm_mon) + ('%02d' % tm_day)
        return int(time.mktime(time.strptime(current_date, '%Y%m%d')))


# get timestamp from given time_sting and format
def get_timestamp_from_string(time_str='', time_format='', tz=8):
    # NOTE: time.mktime regard struct_time as LOCAL TIME
    # default time zone: UTC+8
    with strptime_lock:
        if time_str is not '':
            if time_format == '' and bad_date_pattern.match(time_str):
                time_format = '%Y%m%d'
            if time_format is not '':
                return int(time.mktime(time.strptime(time_str, time_format)) - time.timezone - tz * 3600)
            else:
                date_time = parse(time_str, languages=['zh', 'en'])
                if date_time is not None:
                    return int(time.mktime(date_time.timetuple()) - time.timezone - tz * 3600)
        return 0


# get time string from selectors
def get_time_string_from_selectors(doc=None, selectors={}, date_patterns=None):
    for select in selectors:
        if not date_patterns:
            if doc(select):
                return doc(select).text()
        else:
            if doc(select):
                for pat in date_patterns:
                    if pat.findall(doc(select).text()):
                        return pat.findall(doc(select).text())[0]
    return ''


# get timestamp from selectors
def get_timestamp_from_selectors(doc=None, selectors={}, date_format='', date_patterns=None):
    t = get_time_string_from_selectors(doc, selectors, date_patterns)
    if t is '':
        return 0
    t_stamp = get_timestamp_from_string(t, date_format)
    return t_stamp


# filter the parameters in url
def url_para_filter(url, auto_filtering_url_paras):
    if auto_filtering_url_paras:
        return re.sub(ur'(\?|#).*', u'', url)
    return url


# get a date string of today
def get_day_string(interval_str='', style='normal', offset=0, tz=8):
    # default time zone: UTC+8
    day_stamp = int(time.time() - (24 * 3600) * offset)
    day = time.localtime(day_stamp - time.timezone - tz * 3600)
    ymd = [str(day.tm_year), ('%02d' % day.tm_mon), ('%02d' % day.tm_mday)]
    if style == 'normal':
        return ymd[0] + interval_str + ymd[1] + interval_str + ymd[2]
    elif style == 'inverse':
        return ymd[2] + interval_str + ymd[1] + interval_str + ymd[0]
    elif style == 'american':
        return ymd[1] + interval_str + ymd[2] + interval_str + ymd[0]
    else:
        print 'Unknown style.'
        return ''


def get_offset_by_day_date(start_date, end_date=get_day_string()):
    if start_date:
        start_stamp = get_timestamp_from_string(start_date)
        end_stamp = get_timestamp_from_string(end_date)
        return (end_stamp - start_stamp) / (24 * 3600)
    return 0


def get_facebook_comments_data(app_id, href, **kwargs):
    if not href:
        return None
    r = requests.get(
        "https://www.facebook.com/plugins/feedback.php?api_key=" +
        str(app_id) +
        "&href=" +
        urllib.quote(href, safe='') +
        "&locale=zh_HK&numposts=" + str(100) + "&sdk=joey&version=v2.6"
    )
    search_res = re.findall(ur'(?<="comments":).*?\}(?=,"meta")', r.text)
    if search_res:
        json_res = search_res[0]
    else:
        json_res = None
    print json_res
    return json_res


def get_filtered_facebook_comments_data(app_id, href, page_url, **kwargs):
    res = get_facebook_comments_data(app_id, href)
    if res:
        res = json.loads(res)
        _res = []
        for _comment_id in res['commentIDs']:
            _comment = dict()
            _comment['id'] = _comment_id
            _comment['text'] = res['idMap'][_comment_id]['body']['text']
            _comment['timestamp'] = res['idMap'][_comment_id]['timestamp']['time']
            _comment['author'] = {}
            _author = res['idMap'][res['idMap'][_comment_id]['authorID']]
            _comment['author']['id'] = _author['id']
            _comment['author']['name'] = _author['name']
            if 'uri' in _author:
                _comment['author']['uri'] = _author['uri']
            _comment['targetID'] = res['idMap'][_comment_id]['targetID']
            _comment['page_url'] = page_url
            _comment['comment_source'] = 'facebook'
            _comment['json_string'] = json.dumps(_comment)
            _res.append(_comment)
        return _res
    return None


def within_active_interval(active_times, duration):
    if active_times == 0:
        return False
    _cur_stamp = int(time.time())
    _distance_to_last_point = (_cur_stamp - get_day_stamp()) % ((24 * 3600) / active_times)
    if _distance_to_last_point < duration:
        return True
    return False
