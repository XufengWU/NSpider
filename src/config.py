# -*- coding:utf-8 -*-
import logging

LOGGER_CON = logging.getLogger('scheduler_logger_con')
LOGGER_CON.handlers = []
LOGGER_CON.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
formatter.datefmt = '%Y-%m-%d %H:%M:%S'
console_handler.setFormatter(formatter)
LOGGER_CON.addHandler(console_handler)

LOGGER_FILE = logging.getLogger('scheduler_logger_file')
LOGGER_FILE.handlers = []
LOGGER_FILE.setLevel(logging.DEBUG)
console_handler = logging.FileHandler('logs/spider_scheduler.log')
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
formatter.datefmt = '%Y-%m-%d %H:%M:%S'
console_handler.setFormatter(formatter)
LOGGER_FILE.addHandler(console_handler)

MAX_TASK_QUEUE_SIZE = 20
RSS_MODULE = 'spider_rss'
RSS_SPIDER_CLASS = 'SpiderRSS'

SOURCE_EXTRA_CONFIG = {
    2: {'spider_kwargs': {'PUT_IN_STORAGE': True}},
    8: {'source': 'HKMA', 'spider_kwargs': {'outer_spider_module': 'spiders.spider_hkma', 'outer_spider_class': 'SpiderHKMA', 'PUT_IN_STORAGE': True}}
}

THREAD_NUM_OF_TYPE = {
    'rss': 1
}

FACEBOOK_GRAPH_API_ACCESS_TOKEN = 'EAARj6yZCzHqoBAN1VRjQ0ByQ7zS5cmZCrWZAEqfvK9TpkrRSAWu0X0lwZCtWR2KoE8UIZAoh3gCFbl8n22W8o4aNhbYq0W7FAaauo4M0nv52tU736qeGTG00NdzC3XeZBprqOA5Lt1PxZCOR7AxAIv12ozSfXhmxwqx8PD9yKA0HQZDZD'

DEBUG = True
THREAD_COUNT = 10
SHOW_TIME = True
