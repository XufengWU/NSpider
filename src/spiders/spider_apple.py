# -*- coding:utf-8 -*-
import common_news_spider
import util
import time


class SpiderApple(common_news_spider.CommonNewsSpider):

    def normal_item_solver(self, item, task, response):

        response.encoding = 'utf-8'
        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, u' \|.*')
        t = util.get_day_string(offset=self.OFFSET)
        t_stamp = util.get_timestamp_from_string(t) + time.localtime().tm_hour*3600 + time.localtime().tm_min*60
        category = doc('meta[name=subsection]').attr('content')
        author = ''
        content = util.get_paragraphs_from_selector(doc, '#masterContent p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'AppleNews'
        item.task_no = self.BATCH_NUMBER
        if util.within_active_interval(6, 20*60):
            _comments = util.get_filtered_facebook_comments_data('367495573302576', doc('meta[property="og:url"]').attr('content'), task.url)
            if _comments:
                for _comment in _comments:
                    item.media_list.append(
                        self.NewsItem.MediaItem(media_url=_comment['json_string'], type='comments', description='comments', created_at=item.fetched_at)
                    )

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        day_str = util.get_day_string(offset=offset)
        apple_seed = {'http://hk.apple.nextmedia.com/archive/index/' + day_str + '/index/'}
        spider_apple = SpiderApple('SpiderApple',
                                   apple_seed,
                                   {ur'http://hk\.apple\.nextmedia\.com/.*' + day_str + '/.*'},
                                   THREAD_NUM=15)
        spider_apple.BATCH_NUMBER = util.get_day_stamp() + 10590
        spider_apple.OFFSET = offset
        return spider_apple


if __name__ == '__main__':

    for i in range(22, 52):
        SpiderApple.PUT_IN_STORAGE = False
        SpiderApple.DEFAULT_PUT_IN_FILE = True
        # SpiderApple.OUTPUT_FILE_PATH = 'Apple_' + str(i) + '.json'
        SpiderApple.start_crawling(offset=i, OUTPUT_FILE_PATH='Apple_' + str(i) + '.json')
