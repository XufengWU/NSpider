# -*- coding:utf-8 -*-
from common_news_spider import CommonNewsSpider
import util
from facebook_spider.graph_api_util import GraphApiUtil
import facebook_spider.config
import codecs
import json
import random


class SpiderFacebookGraph(CommonNewsSpider):

    COMMENT_LIKES_LIMIT = 100
    COMMENTS_LIMIT = 50

    token_list = []

    @classmethod
    def append_access_token(cls, url):
        if len(cls.token_list) == 0:
            return url
        access_token = cls.token_list[random.randint(0, len(cls.token_list) - 1)]
        return url + '&access_token=' + access_token

    def normal_solver(self, task, response):
        page_json = json.loads(response.text)
        page_dict = dict()
        page_dict['id'] = page_json['id']
        page_dict['name'] = page_json['name']
        page_dict['fan_count'] = page_json['fan_count']
        page_dict['posts'] = list()
        if 'posts' in page_json:
            posts_data = page_json['posts']['data']
            for post in posts_data:
                data_dict = dict()
                if 'message' in post:
                    data_dict['message'] = post['message']
                    data_dict['created_time'] = post['created_time']
                    data_dict['id'] = post['id']
                if 'likes' in post:
                    self.get_field_data_of_post('likes', post, data_dict)
                if 'comments' in post:
                    self.get_field_data_of_post('comments', post, data_dict)
                page_dict['posts'].append(data_dict)
        current_list = []
        try:
            with codecs.open('facebook_posts_data/' + util.get_day_string() + '.json', 'r', encoding='utf-8') as fr:
                current_list = json.load(fr)
        except IOError:
            pass
        with codecs.open('facebook_posts_data/' + util.get_day_string() + '.json', 'w', encoding='utf-8') as fw:
            for page in current_list:
                if page_dict['id'] == page['id']:
                    current_list.remove(page)
                    break
            current_list.append(page_dict)
            json.dump(current_list, fw)
            fw.close()

    def get_field_data_of_post(self, field, post, data_dict):
        if field in post:
            data_dict[field] = list()
            for entry in post[field]['data']:
                data_dict[field].append(entry)
            if 'next' in post[field]['paging']:
                obj_id = post['id']
                after_cursor = post[field]['paging']['cursors']['after']
                while True:
                    further_data = GraphApiUtil.get_further_data_by_cursor(obj_id, field, after_cursor)
                    if 'data' in further_data:
                        for entry in further_data['data']:
                            data_dict[field].append(entry)
                    if 'after' in further_data:
                        after_cursor = further_data['after']
                    else:
                        break

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        token_list = ['EAAMzwiWLHFABAJToojvbqOzqrxPdfgBP3H4iQUV9Xuq7gUhaRRXcT2mfBPgCRgeSR3LrhS4YRoKC6CwZBAH2xGRrtLWCX9q1vrJZAuyATtlFRZC7nGOIoheSEKor74UZCYMO1r9DJZAF9NuUmMB1jUiOhOJaa5wwZDs',
                      'EAARj6yZCzHqoBAKJbCZA5zrFTjViD09dPfCxIe57Wz8plVb8q8fyFzZACnzT80MiYu6jb448GBztUYhUIPJHbdSEE21ClkNaePMMIgDI5qLmte0o0O4yijY5CNB7ZBtDLbcLWQVQXxZBfpd33a9mHLinFIeypaZAIXWqVFVP7ZCfwZDZD']
        SpiderFacebookGraph.token_list = token_list
        since_stamp = util.get_day_stamp(0)
        _seed = GraphApiUtil.get_seed_urls_from_name_id_dict(since_stamp)
        #_seed = set(list(_seed)[0:1])
        fb_seed = set()
        for s in _seed:
            fb_seed.add(SpiderFacebookGraph.append_access_token(s))
        spider_fb_graph = SpiderFacebookGraph('FacebookGraphSpider', fb_seed, {ur'.*'}, THREAD_NUM=1, MAX_DEPTH=0)
        spider_fb_graph.BATCH_NUMBER = util.get_day_stamp() + 10700
        spider_fb_graph.OFFSET = offset
        spider_fb_graph.FETCH_DELAY = 15
        spider_fb_graph.logger_con = facebook_spider.config.logger_con
        spider_fb_graph.logger_file = facebook_spider.config.logger_file
        return spider_fb_graph

        
if __name__ == '__main__':
    SpiderFacebookGraph.start_crawling()
