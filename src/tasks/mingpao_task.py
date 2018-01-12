# -*- coding:utf-8 -*-
import src.spiders.spider_mingpao
import src.spiders.util as util
import requests
import json
import re

news_list_data_pattern = re.compile(r'(?<=\':).*(?=};)')


def main_task():

    issue_dict_url = 'http://news.mingpao.com/dat/pns/issuelist.js?819181'
    r = requests.get(issue_dict_url)
    json_issue_dict = json.loads(r.text)

    src.spiders.spider_mingpao.SpiderMingPao.PUT_IN_STORAGE = True
    for i in range(util.get_offset_by_day_date('20040627'), util.get_offset_by_day_date('20010101')):
        day_str = util.get_day_string(offset=i)
        if '1 ' + day_str in json_issue_dict['PNS_WEB_TC']:
            issue_id = json_issue_dict['PNS_WEB_TC']['1 ' + day_str]['E']
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
            spider_mingpao = src.spiders.spider_mingpao.SpiderMingPao('SpiderMingPao', mingpao_seed, mingpao_reg,
                                                                      THREAD_NUM=5)
            spider_mingpao.OFFSET = i
            spider_mingpao.logger_file = spider_mingpao.get_file_logger('mingpao_task_log', 'logs/mingpao_task.log')
            spider_mingpao.BATCH_NUMBER = util.get_day_stamp(i) + 10570
            spider_mingpao.start()
        else:
            print 'KEY ERROR: ' + '"1 ' + day_str + '"'


if __name__ == '__main__':
    main_task()
