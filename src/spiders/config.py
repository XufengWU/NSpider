# -*- coding:utf-8 -*-
import os.path
import sys

dir_name = os.path.dirname(__file__)

CHOSEN_SERVER = 'server1'
if len(sys.argv) > 1:
    if sys.argv[1] == 'server1' or sys.argv[1] == 'server2':
        CHOSEN_SERVER = sys.argv[1]
SERVERS_DICT = {
    'server1': 'http://192.168.66.167/api/2/',
    'server2': 'http://192.168.66.168/storage-api/'
}

COMMON_NEWS_SPIDER_CONSOLE_LOG_NAME = 'common_news_spider_console_log'
COMMON_NEWS_SPIDER_FILE_LOG_NAME = 'common_news_spider_file_log'
COMMON_NEWS_SPIDER_LOG_FILE_DIR = dir_name + '/logs/'
if not os.path.exists(COMMON_NEWS_SPIDER_LOG_FILE_DIR):
    os.makedirs(COMMON_NEWS_SPIDER_LOG_FILE_DIR)
COMMON_NEWS_SPIDER_LOG_FILE_PATH = COMMON_NEWS_SPIDER_LOG_FILE_DIR + 'common_news_spider_' + CHOSEN_SERVER + '.log'



