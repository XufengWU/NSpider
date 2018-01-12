# -*- coding:utf-8 -*-
import common_news_spider
import urllib
import re
import sys
import requests
from pyquery import PyQuery as pq
import threading
import win32com.client as win32
import codecs
import traceback
import time
import pythoncom
import os.path
import json
try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
import zipfile
import util

http_pattern = re.compile(r'http://')
prefix = 'http://library.legco.gov.hk:1080'
WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'


class SpiderLegcoRecord(common_news_spider.CommonNewsSpider):

    def docx_to_json(self, path):
        document = zipfile.ZipFile(path)
        xml_content = document.read('word/document.xml')
        document.close()
        tree = XML(xml_content)
        sections = []
        people = None
        search_date_res = re.findall(r'(?<=H)\d{6,8}', path)
        created_at = 0
        if search_date_res:
            if len(search_date_res[0]) == 6:
                search_date_res[0] = '19' + search_date_res[0]
            created_at = util.get_timestamp_from_string(search_date_res[0])
        paragraph_index = 0
        section_index = 0
        current_section = None
        # # remove the texts of tables
        # for tbl in tree.getiterator(WORD_NAMESPACE+'tbl'):
        #     for _child in tbl.findall('.//'):
        #         if _child.text:
        #             print _child.text + ' ' + path
        #             _child.text = ''
        for paragraph in tree.findall('./*/*'):
            texts = [node.text
                     for node in paragraph.getiterator(TEXT)
                     if node.text]
            if texts:
                # paragraphs.append(''.join(texts))
                para_text = ''
                if paragraph.tag == WORD_NAMESPACE + 'tbl':
                    if not re.match(ur'\d*香港立法局.{4,5}年.{1,2}月.{1,2}日\d*', ''.join(texts)):
                        para_text = '** TABLE **'
                elif paragraph.tag == PARA:
                    para_text = ''.join(texts)
                    if re.findall(ur'^[^，]{1,6}議員[^說話]{0,6}：[^\s]+|' +
                                  ur'^.{1,10}：主席|' +
                                  ur'^[^，]{0,10}主席[^說話]{0,6}：|' +
                                  ur'^[^，]{1,8}局長[^說話]{0,6}：|' +
                                  ur'^[^，]{1,8}司長[^說話]{0,6}：|' +
                                  ur'^[^，]{1,6}長官[^說話]{0,6}：|' +
                                  ur'^.{1,10}（譯文）：|' +
                                  ur'^.{1,10}（傳譯）：|' +
                                  ur'^.{1,10}的譯文：|' +
                                  ur'^.{1,10}致辭：',
                                  para_text):
                        split_res = re.split(ur'：|:', para_text)
                        para_text = ''.join(para_text.split(u'：')[1:])
                        if split_res:
                            people = split_res[0]
                            while re.findall(ur'\d+\.|（譯文）|（傳譯）|致辭的譯文$|問題的譯文$|答覆的譯文$|致辭$|答復$|問$|答$|.+?、|(?<=議員).+|動議的.+', people):
                                people = re.sub(ur'\d+\.|（譯文）|（傳譯）|致辭的譯文$|問題的譯文$|答覆的譯文$|致辭$|答復$|問$|答$|.+?、|(?<=議員).+|動議的.+', '', people)
                            if len(people) > 15:
                                self.logger_con.warning('too long people name: ' + people + ' ' + path)
                        if current_section:
                            sections.append(current_section)
                        current_section = {'people': people, 'section_index': section_index, 'created_at': created_at,
                                           'paragraphs': []}
                        section_index += 1
                if current_section and para_text != '':
                    current_section['paragraphs'].append({'paragraph_index': paragraph_index, 'text': para_text})
                paragraph_index += 1
        if current_section and len(current_section['paragraphs']) > 0:
            sections.append(current_section)
        json_f = codecs.open(path[:-4] + 'json', 'w', encoding='utf-8')
        json.dump(sections, json_f)
        json_f.close()
        self.logger_con.info('parsed to json: ' + path)

    def doc_to_docx(self, file_name, word):
        if not os.path.exists(file_name + 'x'):
            doc = word.Documents.Open(file_name)
            doc.SaveAs2(file_name + 'x', FileFormat=12)
            doc.Close()
            os.remove(file_name)
            return True
        self.logger_con.info('exists: ' + file_name + 'x')
        return False

    def convert_docs(self, path):
        word = win32.DispatchEx('Word.Application')
        try:
            for f in os.listdir(path):
                try:
                    if f[-4:] == '.doc':
                        if self.doc_to_docx(path+f, word):
                            self.docx_to_json(path + f + 'x')
                        else:
                            os.remove(path+f)
                    elif f[-4:] == 'docx':
                        self.docx_to_json(path + f)
                except Exception, e:
                    self.logger_con.error(str(e) + ': ' + f)
        finally:
            word.Quit()

    def download_file(self, url, file_name):
        if file_name[:6] == 'doc/CB':
            self.logger_con.warning('not target file: ' + file_name + ' ' + url)
            return
        file_name = re.sub(ur'[^\d\w\.\\/]', '', file_name)
        web_file = urllib.urlopen(url)
        if web_file.url[-4:] == 'DOCX' or web_file.url[-4:] == 'docx':
            file_name += 'x'
        elif web_file.url[-4:] == '.PDF' or web_file.url[-4:] == '.pdf':
            file_name = file_name[:-4] + '.pdf'
        local_file = codecs.open(file_name, 'wb')
        local_file.write(web_file.read())
        web_file.close()
        local_file.close()

    def get_links(self, doc, url=''):
        return []

    def get_url_of_link(self, link, doc, doc_url):
        u = ''
        if link.attr('href'):
            u = link.attr('href')
            if not http_pattern.findall(u):
                u = prefix + u
        return u

    def normal_item_check(self, item, task, response):
        return True

    def normal_item_persistence(self, item, task, response):
        self.logger_con.info(item.title)

    def normal_item_solver(self, item, task, response):
        doc = self.get_doc(response)
        item.title = doc('.bibLinks tr:last-child a').text()
        self.download_file(self.get_url_of_link(doc('.bibLinks tr:last-child a'), None, None),
                           'doc/'+doc('.bibLinks tr:last-child a').text()+'.doc')

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        legco_record_seed = set()
        for i in range(1001, 1001+5):
            legco_record_seed.add('http://library.legco.gov.hk:1080/search~S10*cht?/X{u6703}{u8B70}{u904E}{u7A0B}&SORT=D/X{u6703}{u8B70}{u904E}{u7A0B}&SORT=D&extended=0&SUBKEY=%E6%9C%83%E8%AD%B0%E9%81%8E%E7%A8%8B/1%2C4275%2C4275%2CB/frameset&FF=X{u6703}{u8B70}{u904E}{u7A0B}&SORT=D&extended=0&SUBKEY=%E6%9C%83%E8%AD%B0%E9%81%8E%E7%A8%8B&' +
                                  str(i+1) +
                                  '%2C' +
                                  str(i+1) +
                                  '%2C')
        legco_record_reg = {ur'.+'}
        spider_legco_record = SpiderLegcoRecord('SpiderLegcoRecord',
                                                legco_record_seed,
                                                legco_record_reg,
                                                THREAD_NUM=30,
                                                MAX_DEPTH=0)
        spider_legco_record.BATCH_NUMBER = 0
        spider_legco_record.OFFSET = 0
        spider_legco_record.RETRY_TIMES = 1
        return spider_legco_record


if __name__ == '__main__':
    SpiderLegcoRecord.PUT_IN_STORAGE = False
    _spider = SpiderLegcoRecord.start_crawling()
    time.sleep(1)
    _spider.convert_docs('c://users/benwu/NSpider/src/spiders/doc/')
