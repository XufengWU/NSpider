# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import codecs
import threading
from pyquery import PyQuery as pq

ap_1_pattern = re.compile(ur'附表一')
ap_2_pattern = re.compile(ur'附表二')
ap_3_pattern = re.compile(ur'附表三')
ap_4_pattern = re.compile(ur'附表四')
ap_5_pattern = re.compile(ur'附表五')
ap_6_pattern = re.compile(ur'附表六')


class SpiderWords(common_news_spider.CommonNewsSpider):

    words = set()
    words_lock = threading.Lock()
    a_1 = set()
    a_2 = set()
    a_3 = set()
    a_4 = set()
    a_5 = set()
    a_6 = set()

    def normal_solver(self, task, response):
        doc = pq(response.text)
        titles = doc('.headerWhite[colspan="5"], .headerBlack[bgcolor="#CAC9E4"]').items()
        for title in titles:
            if title.parents('#tblCi'):
                print 'green title: ' + title.text()
                for tr in title.parent().siblings('tr.ks1, tr.ks2').items():
                    if tr('td.ci').text() != '':
                        wd = tr('td.ci').text()
                        with self.words_lock:
                            if wd not in self.words:
                                self.words.add(wd)
                                print wd + ',' + tr('td:last-child').text() + ' ' + task.url
                                with codecs.open(u'小學學習字詞表.txt', 'a', 'utf-8') as fw:
                                    fw.write(wd + ',' + tr('td:last-child').text()+';')
                                    fw.close()
                            else:
                                print 'old word: ' + wd + ' in ' + 'words.txt'
            else:
                print 'purple title: ' + title.text()
                wds_table = title.parents('table').next('table')
                for td in wds_table('td.ci').items():
                    if td.text() != '':
                        for wd in td.text().split(' '):
                            _appendix = None
                            _fp = title.text() + '.txt'
                            if ap_1_pattern.findall(title.text()):
                                _appendix = self.a_1
                            elif ap_2_pattern.findall(title.text()):
                                _appendix = self.a_2
                            elif ap_3_pattern.findall(title.text()):
                                _appendix = self.a_3
                            elif ap_4_pattern.findall(title.text()):
                                _appendix = self.a_4
                            elif ap_5_pattern.findall(title.text()):
                                _appendix = self.a_5
                            elif ap_6_pattern.findall(title.text()):
                                _appendix = self.a_6
                            with self.words_lock:
                                if wd not in _appendix:
                                    _appendix.add(wd)
                                    print wd + ' ' + task.url
                                    with codecs.open(_fp, 'a', 'utf-8') as fw:
                                        fw.write(wd+',')
                                        fw.close()
                                else:
                                    print 'old word: ' + wd + ' in ' + _fp

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        wd_seed = set()
        for i in range(1000, 4762):
            wd_seed.add('http://www.edbchinese.hk/lexlist_ch/result.jsp?id='+str(i))
        spider_words = SpiderWords('SpiderWords', wd_seed, {ur'http://www\.edbchinese\.hk/lexlist_ch/result\.jsp\?id=\d+'},
                                   THREAD_NUM=30)
        spider_words.BATCH_NUMBER = util.get_day_stamp() + 222
        return spider_words


if __name__ == '__main__':

    SpiderWords.PUT_IN_STORAGE = False
    SpiderWords.ADD_MEDIA = False
    SpiderWords.start_crawling()
