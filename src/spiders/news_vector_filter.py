# -*- coding: utf-8 -*-

import re
import json
import requests

FILTER_VALUES = [
    {
        'name': 'area',
        'values': [
            'mainland',
            'hk',
            'macao',
            'tw',
            'foreign'
        ]
    },
    {
        'name': 'essence',
        'values': [
            'news',
            'non-news'
        ]
    },
    {
        'name': 'topic',
        'values': [
            'politics',
            'economy',
            'culture & life',
            'sports',
            'entertainment',
            'IT & tech',
            'social'
        ]
    },
    {
        'name': 'language',
        'values': [
            'chinese',
            'english'
        ]
    },
    {
        'name': 'source',
        'values': [
            u'HK01',
            u'appledaily.hk',
            u'HKEJ',
            u'SingTao',
            u'BastillePost',
            u'ZaoBao',
            u'Sina',
            u'Reuters CN',
            u'HKET',
            u'AM730',
            u'MetroFinance',
            u'RTHK',
            u'mingpao',
            u'PassionTimes',
            u'SkyPost',
            u'TVB',
            u'WenWei',
            u'Xinhua',
            u'OrientalDaily',
            u'HKCNA',
            u'NowNews',
            u'TaKungPao',
            u'CableNews',
            u'Finet',
            u'StandNews',
            u'法新社',
            u'HeadlineNews',
            u'HKCD',
            u'Initium',
            u'NOWnews',
            u'CommercialRadio',
            u'Macao',
            u'852',
            u'SpeakOut',
            u'Peanut',
            u'LocalPress',
            u'HKMA',
            u'InMedia',
            u'EastWeek',
            u'GovNews',
            u'CRN',
            u'VJMedia',
            u'People',
            u'Bauhinia',
            u'BBC Chinese',
            u'HKEDB',
            u'FMCOPRC',
            u'HKPRI',
            u'JD Online',
            u'LegislativeCouncil',
            u'MetroHK',
            u'SunDaily',
            u'RFI',
            u'UBeat',
            u'WSJ',
            u'Y28',
            u'Unwire',
            u'HKSilicon',
            u'Locpg',
            u'SCMP',
            u'NewCenturyForum',
            u'Yahoo'
            u'AM730 Column',
            u'ChinaDaily',
            u'HKFP',
            u'CNBC',
            u'TMHK',
            u'Standard',
            u'HouseNewsBlogger',
            u'Cool3C',
            u'CitizenNews',
            u'NewsLens'
        ]
    }
]

# dictionaries to determine the filter values by news attribute as key with priorities
# filter key -> priority queue by attributes
# attribute name -> attributes sharing a same map
FILTER_KEYWORD_PRIORITY_MAP = {
    'area': [
        {
            'attr_name': ['source'],
            'keyword_map': {
                'Macao': 2
            }
        },
        {
            'attr_name': ['category'],
            'keyword_map': {
                u'内地': 0,
                u'內地': 0,
                u'中国': 0,
                u'中國': 0,
                u'大陸': 0,
                u'大陆': 0,
                u'香港': 1,
                u'港聞': 1,
                u'港闻': 1,
                u'本地': 1,
                u'澳門': 2,
                u'澳门': 2,
                u'澳聞': 2,
                u'澳闻': 2,
                u'台灣': 3,
                u'台湾': 3,
                u'亞洲': 4,
                u'亚洲': 4,
                u'國際': 4,
                u'国际': 4,
                u'海外': 4,
                u'Global': 4
            }
        },
        {
            'attr_name': ['title'],
            'keyword_map': {
                u'内地': 0,
                u'內地': 0,
                u'大陸': 0,
                u'大陆': 0,
                u'香港': 1,
                u'本港': 1,
                u'澳門': 2,
                u'澳门': 2,
                u'台灣': 3,
                u'台湾': 3,
                u'亞洲': 4,
                u'亚洲': 4,
                u'歐洲': 4,
                u'欧洲': 4,
                u'歐盟': 4,
                u'欧盟': 4,
                u'國際': 4,
                u'国际': 4,
                u'海外': 4
            }
        }
    ],
    'essence': [
        {
            'attr_name': ['category', 'title'],
            'keyword_map': {
                u'01博評': 1,
                u'01觀點': 1,
                u'觀點': 1,
                u'观点': 1,
                u'評論': 1,
                u'评论': 1,
                u'社論': 1,
                u'社论': 1,
                u'言論': 1,
                u'言论': 1,
                u'觀察': 1,
                u'專欄': 1,
                u'专栏': 1,
                u'博客': 1,
                u'小城小事': 1,
                u'故事': 1,
                u'小说': 1,
                u'小說': 1,
                u'新園地': 1,
                u'新园地': 1,
                u'副刊': 1,
                u'（文：.+?）': 1
            }
        }
    ],
    'topic': [
        {
            'attr_name': ['category'],
            'keyword_map': {
                u'選舉': 0,
                u'选举': 0,
                u'政治': 0,
                u'政坛': 0,
                u'政壇': 0,
                u'政府': 0,
                u'政经': 0,
                u'政經': 0,
                u'政情': 0,
                u'政纲': 0,
                u'政綱': 0,
                u'社運': 0,
                u'社运': 0,
                u'财经': 1,
                u'財經': 1,
                u'經濟': 1,
                u'经济': 1,
                u'金融': 1,
                u'投資': 1,
                u'投资': 1,
                u'地產': 1,
                u'地产': 1,
                u'行業': 1,
                u'行业': 1,
                u'大市': 1,
                u'市場': 1,
                u'市场': 1,
                u'港股': 1,
                u'股市': 1,
                u'钱财': 1,
                u'錢財': 1,
                u'業績': 1,
                u'业绩': 1,
                u'文化': 2,
                u'讀書': 2,
                u'读书': 2,
                u'藝術': 2,
                u'艺术': 2,
                u'藝海': 2,
                u'艺海': 2,
                u'文藝': 2,
                u'文艺': 2,
                u'艺文': 2,
                u'藝文': 2,
                u'電影': 2,
                u'电影': 2,
                u'新園地': 2,
                u'新园地': 2,
                u'生活': 2,
                u'Life': 2,
                u'副刊(?!\\科技)': 2,
                u'Sports': 3,
                u'體育': 3,
                u'体育': 3,
                u'体坛': 3,
                u'體壇': 3,
                u'nba': 3,
                u'NBA': 3,
                u'足球': 3,
                u'馬經': 3,
                u'马经': 3,
                u'娛樂': 4,
                u'娱乐': 4,
                u'娛圈': 4,
                u'娱圈': 4,
                # u'科學': 5,
                # u'科学': 5,
                # u'科技$': 5,
                # u'科技(?!/game|/movie|/column|/walk|/unwire_podcast|/gadgets|/japan-gadget|/photogism|玩物)': 5,
                # u'技術': 5,
                # u'技术': 5,
                u'電腦與科技': 5,
                u'程式': 5,
                u'程序': 5,
                u'software': 5,
                u'wireless-home': 5,
                u'mobile-phone': 5,
                u'App': 5,
                u'app': 5,
                u'Android': 5,
                u'iOS': 5,
                u'ios': 5,
                u'IT': 5,
                u'Google': 5,
                u'手機': 5,
                u'手机': 5,
                u'社交網絡': 5,
                u'開發': 5,
                u'電子': 5,
                u'社會': 6,
                u'社会': 6,
                u'政社': 6,
                u'Plastic': 6
            }
        },
        {
            'attr_name': ['title'],
            'keyword_map': {
                u'選舉': 0,
                u'选举': 0,
                u'政治': 0,
                u'政坛': 0,
                u'政壇': 0,
                u'政府': 0,
                u'政经': 0,
                u'政經': 0,
                u'政情': 0,
                u'政纲': 0,
                u'政綱': 0,
                u'国务院': 0,
                u'國務院': 0,
                u'民主党': 0,
                u'民主黨': 0,
                u'自由黨': 0,
                u'自由党': 0,
                u'特朗普': 0,
                u'歐盟': 0,
                u'欧盟': 0,
                u'外长': 0,
                u'外長': 0,
                u'总统': 0,
                u'總統': 0,
                u'金正恩': 0,
                u'总理': 0,
                u'總理': 0,
                u'特首': 0,
                u'梁振英': 0,
                u'曾俊华': 0,
                u'曾俊華': 0,
                u'林鄭': 0,
                u'林郑': 0,
                u'行政長官': 0,
                u'行政长官': 0,
                u'內戰': 0,
                u'内战': 0,
                u'国台办': 0,
                u'國台辦': 0,
                u'市委': 0,
                u'市長': 0,
                u'市长': 0,
                u'极右': 0,
                u'極右': 0,
                ur'[^冠]軍': 0,
                ur'[^冠]军': 0,
                u'财经': 1,
                u'財經': 1,
                u'經濟': 1,
                u'经济': 1,
                u'金融': 1,
                u'投資': 1,
                u'投资': 1,
                u'地產': 1,
                u'地产': 1,
                u'行業': 1,
                u'行业': 1,
                u'產業': 1,
                u'产业': 1,
                u'大市': 1,
                u'市場': 1,
                u'市场': 1,
                u'港股': 1,
                u'股市': 1,
                u'股票': 1,
                u'PMI': 1,
                u'成交量': 1,
                u'完工': 1,
                u'天主教': 2,
                u'展覽': 2,
                u'展览': 2,
                u'演出': 2,
                u'生活小竅門': 2,
                u'生活小窍门': 2,
                u'nba': 3,
                u'NBA': 3,
                u'足球': 3,
                u'籃球': 3,
                u'篮球': 3,
                # u'研发': 5,
                # u'研發': 5,
                # u'科研': 5,
                # u'技術': 5,
                # u'技术': 5,
                u'智能': 5,
                u'apps': 5,
                u'罷工': 6,
                u'罢工': 6,
                u'墜樓': 6,
                u'墮樓': 6,
                u'坠楼': 6,
                u'自杀': 6,
                u'自殺': 6,
                u'老翁': 6,
                u'市民': 6,
                u'火警': 6,
                u'拘': 6,
                u'男子': 6,
                u'女子': 6,
                u'漢': 6,
                u'婦': 6,
                u'罪成': 6,
                u'判刑': 6,
                u'判囚': 6,
                u'\d歲': 6,
                u'\d岁': 6,
                u'\d旬': 6
            }
        },
        {
            'attr_name': ['source'],
            'keyword_map': {
                'HKET': 1
            }
        }
    ],
    'language': [
        {
            'attr_name': ['source'],
            'keyword_map': {
                'SCMP': 1
            }
        }
    ],
    'source': [
        {
            'attr_name': ['source'],
            'keyword_map': {
                u'SkyPost': 14,
                u'晴報': 14,
                u'StandNews': 24,
                u'CableNews': 22,
                u'Peanut': 34,
                u'JD Online': 48,
                u'GovNews': 39,
                u'GovInfoNews': 39,
                u'Y28': 55,
                u'FMCOPRC': 46,
                u'Bauhinia': 43,
                u'TaKungPao': 21,
                u'AM730': 9,
                u'CRN': 40,
                u'SingTao': 3,
                u'星島日報': 3,
                u'852': 32,
                u'InMedia': 37,
                u'BBC Chinese': 44,
                u'HK01': 0,
                u'Xinhua': 17,
                u'HeadlineNews': 26,
                u'LegislativeCouncil': 49,
                u'WenWei': 16,
                u'HKPRI': 47,
                u'CommercialRadio': 30,
                u'MetroFinance': 10,
                u'NOWnews': 29,
                u'NOWnews 娛樂': 29,
                u'NOWnews 新聞': 29,
                u'Sina': 6,
                u'Reuters CN': 7,
                u'WSJ': 54,
                u'HKEDB': 45,
                u'RTHK': 11,
                u'香港電台': 11,
                u'appledaily.hk': 1,
                u'AppleNews': 1,
                u'ZaoBao': 5,
                u'MetroHK': 50,
                u'法新社': 25,
                u'OrientalDaily': 18,
                u'東方日報': 18,
                u'SunDaily': 51,
                u'HKET': 8,
                u'經濟日報': 8,
                u'RFI': 52,
                u'PassionTimes': 13,
                u'mingpao': 12,
                u'EastWeek': 38,
                u'NowNews': 20,
                u'now.com 體育': 20,
                u'now.com 新聞': 20,
                u'VJMedia': 41,
                u'HKCNA': 19,
                u'BastillePost': 4,
                u'LocalPress': 35,
                u'People': 42,
                u'HKCD': 27,
                u'HKMA': 36,
                u'UBeat': 53,
                u'Initium': 28,
                u'端傳媒': 28,
                u'Finet': 23,
                u'HKEJ': 2,
                u'信報財經新聞': 2,
                u'TVB': 15,
                u'Macao': 31,
                u'SpeakOut': 33,
                u'Unwire': 56,
                u'HKSilicon': 57,
                u'Locpg': 58,
                u'SCMP': 59,
                u'NewCenturyForum': 60,
                u'Yahoo': 61,
                u'AM730 Column': 62,
                u'ChinaDaily': 63,
                u'HKFP': 64,
                u'CNBC': 65,
                u'TMHK': 66,
                u'Standard': 67,
                u'HouseNewsBlogger': 68,
                u'Cool3C': 69,
                u'CitizenNews': 70,
                u'NewsLens': 71
            }
        }
    ]
}

non_eng_pattern = re.compile(r'[^a-zA-Z\s\n\t.,\'\"]')


class NewsVectorFilter:

    kw_patterns = dict()

    def __init__(self):
        pass

    @classmethod
    def get_vector(cls, news_item, auto_cat=False):
        _dict = {}
        for filt in FILTER_VALUES:
            k = filt['name']
            # -1 means unknown
            _dict[k] = -1
            attr_map_arr = FILTER_KEYWORD_PRIORITY_MAP[k]
            for attr_map in attr_map_arr:
                for attr in attr_map['attr_name']:
                    kw_map = attr_map['keyword_map']
                    for kw in kw_map:
                        try:
                            attr_val = news_item.__dict__[attr]
                            if attr_val.__class__ == str:
                                attr_val = attr_val.decode('utf-8')
                            if kw in cls.kw_patterns:
                                kw_pattern = cls.kw_patterns[kw]
                            else:
                                kw_pattern = re.compile(kw)
                                cls.kw_patterns[kw] = kw_pattern
                            if kw_pattern.findall(attr_val):
                                _dict[k] = kw_map[kw]
                                break
                        except Exception, e:
                            raise
                    if _dict[k] >= 0:
                        break
                if _dict[k] >= 0:
                    break
        if _dict['language'] < 0:
            if non_eng_pattern.findall(news_item.title):
                _dict['language'] = 0
            else:
                _dict['language'] = 1
        if _dict['essence'] < 0:
            _dict['essence'] = 0
        if _dict['area'] < 0:
            _dict['area'] = 1
        if auto_cat and _dict['topic'] < 0:
            _cat = cls.get_generated_category(news_item.title+news_item.content)
            try:
                _cat_ind = FILTER_VALUES[2]['values'].index(_cat)
                _dict['topic'] = _cat_ind
            except ValueError:
                if _cat == 'Unknown':
                    _dict['topic'] = -1
                else:
                    raise
        vec = list()
        vec.append(_dict['area']+1)
        vec.append(_dict['essence']+1)
        vec.append(_dict['topic']+1)
        vec.append(_dict['language']+1)
        vec.append(_dict['source']+1)
        return vec

    @classmethod
    def get_dict_by_vector(cls, vector):
        _d = {}
        for i in range(len(vector)):
            if vector[i] == 0:
                _d[FILTER_VALUES[i]['name']] = 'Unknown'
            else:
                _d[FILTER_VALUES[i]['name']] = FILTER_VALUES[i]['values'][vector[i]-1]
        return _d

    @classmethod
    def get_dict_by_news_item(cls, news_item, auto_cat=False):
        v = cls.get_vector(news_item, auto_cat)
        d = cls.get_dict_by_vector(v)
        return d

    @classmethod
    def get_generated_category(cls, text, q_len=200):
        try:
            r = requests.get('http://192.168.66.168/text-api/get-category', {'text': text[0:q_len]})
            if r and r.text:
                r_d = json.loads(r.text)
                if r_d['code'] and 'category' in r_d:
                    return r_d['category']
            return 'Unknown'
        except Exception, e:
            raise

    class NewsItem:

        def __init__(self):
            self.raw = ''
            self.title = ''
            self.t = ''
            self.category = ''
            self.fetched_at = 0
            self.t_stamp = 0
            self.author = ''
            self.content = ''
            self.url = ''
            self.source = ''
            self.task_no = 0
            self.media_list = []


if __name__ == '__main__':
    item = NewsVectorFilter.NewsItem()
    item.source = 'Sina'
    item.category = u'政治'
    item.title = u'Hello'
    vector_filter = NewsVectorFilter()
    vector = vector_filter.get_vector(item)
    print vector
    _dict = vector_filter.get_dict_by_vector(vector)
    print _dict
