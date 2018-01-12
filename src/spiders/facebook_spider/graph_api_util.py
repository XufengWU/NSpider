# -*- coding:utf-8 -*-
import codecs
import copy
import json
import time
import re
import facebook
import requests
import config

name_id_dict_path = config.NAME_ID_DICT_PATH
logger_con = config.logger_con
logger_file = config.logger_file

link_pattern = re.compile(u'http.*')
id_pattern = re.compile(u'\d+')


def is_a_link(line):
    if link_pattern.match(line):
        return True
    return False


class GraphApiUtil:

    access_token = ''

    def __init__(self, access_token):
        self.__class__.access_token = access_token

    @classmethod
    def get_page_search_result(cls, keyword, access_token):
        r = requests.get('https://graph.facebook.com/search?q=' + keyword +
                         '&type=page&fields=name,category,link&limit=10' +
                         '&access_token=' + access_token)
        return json.loads(r.text)

    @classmethod
    def get_name_links(cls, access_token=None, name_list=None):
        if not access_token:
            access_token = cls.access_token
        if not name_list:
            name_list = cls.read_name_list()
        with codecs.open('name_links.txt', 'w+', encoding='utf-8') as f:
            for name in name_list:
                f.write(name + '\n')
                search_result_json = cls.get_page_search_result(name, access_token)
                for entry in search_result_json['data']:
                    if entry['category'] != 'Interest':
                        f.write(entry['link'] + ' ' + entry['id'] + '\n')
            time.sleep(1)
            f.close()

    @classmethod
    def read_name_id_dict(cls):
        name_id_dict = dict()
        with codecs.open(name_id_dict_path, 'r', encoding='utf-8') as f:
            current_name = None
            while True:
                line = f.readline()
                if not line:
                    break
                if not id_pattern.match(line):
                    current_name = re.sub('\n', '', line)
                    name_id_dict[current_name] = None
                else:
                    name_id_dict[current_name] = re.sub('\n', '', line)
            f.close()
        return name_id_dict

    @classmethod
    def collect_news(cls, name_link_dict, access_token):
        pass

    @classmethod
    def read_name_list(cls):
        name_list = list()
        with codecs.open('name_list.txt', encoding='utf-8') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                name_list.append(re.sub(ur'[\r\n]', u'', line))
            f.close()
        return name_list

    @classmethod
    def get_rough_name_id_dict_from_name_links(cls):
        with codecs.open('name_links.txt', 'r', encoding='utf-8') as f:
            with codecs.open(name_id_dict_path, 'w+', encoding='utf-8') as fw:
                is_new_name = False
                while True:
                    line = f.readline()
                    if not line:
                        break
                    if is_a_link(line):
                        if is_new_name:
                            _id = line.split(' ')[1]
                            fw.write(_id)
                            is_new_name = False
                    else:
                        fw.write(line)
                        is_new_name = True
                fw.close()
            f.close()

    @classmethod
    def get_seed_urls_from_name_id_dict(cls, since_stamp, query=None):
        if not query:
            query = '?fields=name,fan_count,likes,posts.since(' + str(since_stamp) + '){message,created_time,likes.limit(' + str(
                config.COMMENT_LIKES_LIMIT) + '),comments.limit(' + str(config.COMMENTS_LIMIT) + ')}'
        seed_urls = set()
        name_id_dict = GraphApiUtil.read_name_id_dict()
        for v in name_id_dict.values():
            if v:
                seed_urls.add('https://graph.facebook.com/' + v + query)
        return seed_urls

    @classmethod
    def get_further_data_by_cursor(cls, obj_id, field, cursor):
        r = requests.get('https://graph.facebook.com/' + obj_id + '?fields=' + field + '.after(' + cursor + ')')
        data_json = json.loads(r.text)
        further_data = dict()
        if field in data_json:
            further_data['data'] = data_json[field]['data']
            if 'paging' in data_json and 'next' in data_json['paging']:
                further_data['after'] = data_json['paging']['cursors']['after']
        return further_data

    @classmethod
    def get_element_data(cls, element_id, fields):
        r = requests.get('https://graph.facebook.com/' + str(element_id) +
                         '?fields=' + fields +
                         '&access_token=' + cls.access_token)
        return r.text


if __name__ == '__main__':
    GraphApiUtil.access_token = 'EAARj6yZCzHqoBAN1VRjQ0ByQ7zS5cmZCrWZAEqfvK9TpkrRSAWu0X0lwZCtWR2KoE8UIZAoh3gCFbl8n22W8o4aNhbYq0W7FAaauo4M0nv52tU736qeGTG00NdzC3XeZBprqOA5Lt1PxZCOR7AxAIv12ozSfXhmxwqx8PD9yKA0HQZDZD'
    # seeds = GraphApiUtil.get_seed_urls_from_name_id_dict()
    # seeds = list(seeds)[0:5]
    # for seed in seeds:
    #     print seed
    print json.dumps(GraphApiUtil.get_element_data('710476795704610', 'name,feed{comments,link}'))




