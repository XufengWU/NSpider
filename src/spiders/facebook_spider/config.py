# -*- coding:utf-8 -*-
import logging

# logging
LOG_FILE = 'logs/facebook_spider.log'
logger_con = logging.getLogger('facebook_spider_console_log')
logger_con.setLevel(logging.DEBUG)
logger_file = logging.getLogger('facebook_spider_file_log')
logger_file.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(filename=LOG_FILE)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger_con.addHandler(console_handler)
logger_file.addHandler(file_handler)

# path of name-id dict file
NAME_ID_DICT_PATH = r'c:\Users\benwu\NSpider\src\spiders\facebook_spider\name_id_dict.txt'

# limits of query
COMMENT_LIKES_LIMIT = 100
COMMENTS_LIMIT = 50
