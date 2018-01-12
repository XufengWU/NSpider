# -*- coding:utf-8 -*-
import spiders.facebook_spider.graph_api_util as graph_util
import spiders.util as util
import requests
import spiders.storage as storage
import json
import codecs
import config
import time
import re


class FacebookPageCommentsCollector:

    ACTIVE_TIMES_PER_DAY = 12
    PAGE_ID_SOURCE_DICT = {
        '105259197447': 'AppleNews',
        '710476795704610': 'StandNews',
        '466505160192708': 'Initium'
    }

    def __init__(self, access_token, id):
        self.graph = graph_util.GraphApiUtil(access_token)
        self.current_id = id

    def get_raw_page_json(self, _id, _fields=None):
        if not _fields:
            _fields = 'name,feed{comments{comments,message,from,created_time},link}'
        _res = self.graph.get_element_data(_id, _fields)
        return _res

    def modify_url(self, url):
        _url = url
        if self.current_id == '710476795704610':
            _url = re.sub(r'https', 'http', _url)
            _url = re.sub(r'://thestand', '://www.thestand', _url)
        return _url

    def valid_page_url(self, url):
        url = self.modify_url(url)
        if storage.url_exists(url):
            return url
        else:
            r = requests.get(url)
            url = self.modify_url(r.url)
            if storage.url_exists(url):
                return url
        return False

    def get_filtered_comments(self, post):
        if 'link' in post:
            _link = post['link']
            _comments = []
            _url = self.valid_page_url(_link)
            if _url:
                if 'comments' in post:
                    for _c in post['comments']['data']:
                        _comment = dict()
                        _comment['id'] = _c['id']
                        _comment['text'] = _c['message']
                        _comment['timestamp'] = str(util.get_timestamp_from_string(_c['created_time'])+8*3600)
                        _author = _c['from']
                        _author['uri'] = 'https://www.facebook.com/app_scoped_user_id/' + _author['id'] + '/'
                        _comment['author'] = _author
                        _comment['targetID'] = post['id']
                        _comment['page_url'] = _url
                        _comment['comment_source'] = 'facebook'
                        if 'comments' in _c:
                            for _inner_c in _c['comments']['data']:
                                _sub_comment = dict()
                                _sub_comment['id'] = _inner_c['id']
                                _sub_comment['text'] = _inner_c['message']
                                _sub_comment['timestamp'] = str(util.get_timestamp_from_string(_inner_c['created_time'])+8*3600)
                                _author = _inner_c['from']
                                _author['uri'] = 'https://www.facebook.com/app_scoped_user_id/' + _author['id'] + '/'
                                _sub_comment['author'] = _author
                                _sub_comment['targetID'] = _comment['id']
                                _sub_comment['page_url'] = _url
                                _sub_comment['comment_source'] = 'facebook'
                                _sub_comment['json_string'] = json.dumps(_sub_comment)
                                print _sub_comment['json_string']
                                _comments.append(_sub_comment)
                        _comment['json_string'] = json.dumps(_comment)
                        print _comment['json_string']
                        _comments.append(_comment)
                    return _comments
        return None

    def persist_comments(self, comments):
        if comments:
            _cur_json = None
            with codecs.open('fb_comments.json', 'r') as fr:
                _cur_json = fr.read()
                fr.close()
            if _cur_json == '':
                _cur_json = '[]'
            with codecs.open('fb_comments.json', 'w') as fw:
                fw.write(_cur_json[:-1])
                for c in comments:
                    if _cur_json[-1] == '[':
                        fw.write(c['json_string'])
                    else:
                        fw.write(','+c['json_string'])
                fw.write(']')

    def solve_comments(self, post_data):
        for post in post_data['feed']['data']:
            _comments = self.get_filtered_comments(post)
            self.persist_comments(_comments)

    @classmethod
    def solve_page(cls, _id):
        print 'solving ' + _id
        _collector = FacebookPageCommentsCollector(config.FACEBOOK_GRAPH_API_ACCESS_TOKEN, _id)
        _j = _collector.get_raw_page_json(_id)
        if not _j:
            print 'no response or too large data required. try again.'
            _j = _collector.get_raw_page_json(_id, 'name,feed.limit(10){comments{comments,message,from,created_time},link}')
        try:
            _post_data = json.loads(_j)
            if 'error' in _post_data:
                print 'error in solving ' + _id
            else:
                _collector.solve_comments(_post_data)
        except ValueError, e:
            print e

    @classmethod
    def main(cls):
        _round_done = True
        while True:
            if util.within_active_interval(cls.ACTIVE_TIMES_PER_DAY, 60*60):
                if not _round_done:
                    print 'start round ' + str(time.localtime().tm_hour) + ':' + str(time.localtime().tm_min)
                    for _id in cls.PAGE_ID_SOURCE_DICT:
                        cls.solve_page(_id)
                    print 'round done ' + str(time.localtime().tm_hour) + ':' + str(time.localtime().tm_min)
                    _round_done = True
            else:
                _round_done = False
            print 'waiting ' + str(time.localtime().tm_hour) + ':' + str(time.localtime().tm_min)
            time.sleep(10*60)


if __name__ == '__main__':
    FacebookPageCommentsCollector.main()
    # FacebookPageCommentsCollector.solve_page('105259197447')