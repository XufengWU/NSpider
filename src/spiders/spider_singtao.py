# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time


t_pattern = re.compile(ur'\d\d\d\d-\d\d-\d\d')
t_pattern_long = re.compile(ur'\d\d\d\d-\d\d-\d\d \d\d:\d\d')
instant_pattern = re.compile(ur'http://std\.stheadline\.com/instant/articles/detail/\d+.+')
instant_cat_pattern = re.compile(ur'http://std\.stheadline\.com/instant/articles/listview/.*')
incomplete_pattern = re.compile(ur'news-content\.php\?.*')
instant_body_pattern = re.compile(ur'/detail/\d+-.+')


class SpiderSingTao(common_news_spider.CommonNewsSpider):

    def __init__(self, name='NewsSpider', seed=None, reg=None, MAX_DEPTH=1, THREAD_NUM=1, cats={}):
        common_news_spider.CommonNewsSpider.__init__(self, name, seed, reg, MAX_DEPTH, THREAD_NUM)
        self._cats = cats

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if incomplete_pattern.match(u.encode('utf-8')):
                u = 'http://std.stheadline.com/daily/' + u
            elif instant_pattern.match(u.encode('utf-8')):
                u = re.sub(ur'\.\./instant/', u'', u)
            else:
                u = ''
        return u

    def adjust_task(self, task):
        old_url = task.url
        task.url = re.sub(ur'\.\./instant/', u'', task.redirected_url)
        self.logger_con.info("original task of " + old_url + " was adjusted to " + task.url)
        self.logger_file.info("original task of " + old_url + " was adjusted to " + task.url)

    def page_filter(self, doc, url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if url is not None and reg_pattern.match(url.encode('utf-8')):
                if re.findall(t_pattern_long, doc('div.date').text()):
                    t = re.findall(t_pattern_long, doc('div.date').text())[0]
                    t_stamp = int(time.mktime(time.strptime(t.encode('utf-8'), '%Y-%m-%d %H:%M')))
                    tm_day = time.localtime().tm_mday
                    search_offset = self.OFFSET
                    if tm_day > search_offset:
                        tm_day -= search_offset
                    else:
                        tm_day = 1
                    current_date = str(time.localtime().tm_year) + ('%02d' % time.localtime().tm_mon) + ('%02d' % tm_day)
                    current_stamp = int(time.mktime(time.strptime(current_date, "%Y%m%d")))
                    if t_stamp >= current_stamp:
                        wanted = True
                elif re.findall(t_pattern, doc('div.date').text()):
                    t = re.findall(t_pattern, doc('div.date').text())[0]
                    t_stamp = int(time.mktime(time.strptime(t.encode('utf-8'), '%Y-%m-%d')))
                    tm_day = time.localtime().tm_mday
                    search_offset = self.OFFSET
                    if tm_day > search_offset:
                        tm_day -= search_offset
                    else:
                        tm_day = 1
                    current_date = str(time.localtime().tm_year) + ('%02d' % time.localtime().tm_mon) + ('%02d' % tm_day)
                    current_stamp = int(time.mktime(time.strptime(current_date, "%Y%m%d")))
                    if t_stamp >= current_stamp:
                        wanted = True
                else:
                    wanted = True
        return wanted

    def task_filter(self, doc, url, doc_url):
        return self.page_filter(doc, url)

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, ur' -- 星島日報')
        t = ''
        t_stamp = 0
        if re.findall(t_pattern_long, doc('div.date').text()):
            t = re.findall(t_pattern_long, doc('div.date').text())[0]
            t_stamp = int(time.mktime(time.strptime(t.encode('utf-8'), '%Y-%m-%d %H:%M')))
        elif re.findall(t_pattern, doc('div.date').text()):
            t = re.findall(t_pattern, doc('div.date').text())[0]
            t_stamp = int(time.mktime(time.strptime(t.encode('utf-8'), '%Y-%m-%d')))
        category = ''
        if doc('input[id=comscore_catid]').attr('value') in self._cats:
            category = self._cats[doc('input[id=comscore_catid]').attr('value')]
        elif doc('a.margin-l-r-5'):
            category = doc('a.margin-l-r-5').text()
        content = util.get_paragraphs_from_selector(doc, 'div.paragraph p')
        author = ''
        current_date = str(time.localtime().tm_year) + ('%02d' % time.localtime().tm_mon) + (
        '%02d' % time.localtime().tm_mday)
        if (not instant_pattern.match(task.url)) and t_stamp >= int(time.mktime(time.strptime(current_date, "%Y%m%d"))):
            t_stamp = int(time.time())

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'SingTao'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.main figure img').items():
            if img.attr('src') != '':
                media_u = img.attr('src')
                des = ''
                if img.attr('alt'):
                    des = img.attr('alt')
                media = self.NewsItem.MediaItem(media_url=media_u, type='image', description=des,
                                                created_at=item.fetched_at)
                item.media_list.append(media)
        for a in doc('iframe').items():
            if a.attr('src') and re.match(r'.*youtube\.com.+', a.attr('src')):
                media_u = a.attr('src')
                if re.match(r'//.+', media_u):
                    media_u = 'http:' + media_u
                media = self.NewsItem.MediaItem(media_url=media_u, type='youtube', description='youtube',
                                                created_at=item.fetched_at)
                item.media_list.append(media)
        # util.updata_facebook_comments('1402188136474239', doc('div.fb-comments').attr('data-href'))

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        cats = dict()
        cats['105'] = '海外綜合'
        cats['102'] = '新聞專輯'
        singtao_seed = {'http://std.stheadline.com/'}
        util.add_hrefs('http://std.stheadline.com/', selectors={'#navbar ul.nav li.has-children > a'}, seeds=singtao_seed)
        '''
        id_pattern = re.compile(ur'(?<=php\?cat=)\d+')
        for cat in d('ul.sub-menu a').items():
            if re.findall(id_pattern, cat.attr('href')):
                cats[re.findall(id_pattern, cat.attr('href'))[0]] = cat.text()
            if instant_cat_pattern.match(cat.attr('href')):
                singtao_seed.add(cat.attr('href'))
        for k, v in cats.iteritems():
            singtao_seed.add('http://std.stheadline.com/daily/section-list.php?cat=' + k)
        '''
        spider_singtao = SpiderSingTao('SpiderSingTao',
                                       singtao_seed,
                                       {ur'(http://std\.stheadline\.com/daily/news-content\.php.*)|(http://std\.stheadline\.com/instant/articles/detail/\d+.*)'},
                                       THREAD_NUM=1,
                                       cats=cats)
        spider_singtao.FETCH_DELAY = 0.5
        spider_singtao.BATCH_NUMBER = util.get_day_stamp() + 10060
        spider_singtao.OFFSET = offset
        return spider_singtao


if __name__ == '__main__':

    SpiderSingTao.PUT_IN_STORAGE = False
    SpiderSingTao.start_crawling()







