# -*- coding:utf-8 -*-
import json
import requests
import facebook
import logging
import codecs
import config
from graph_api_util import GraphApiUtil


my_token = 'EAAMzwiWLHFABANvUJwhiWp3bxAYlQPECWM1Y8HhWUen4PcorEubbvxwU3Ga2rJrYLq2iYwx0zh9FRZAEY3Uf1wacE8hOZC2875zTncNZAPI9ZAluLpIIgeYjDRWTxwsCs5McgjTDBw15TTifg7jUxbjZAERugJ6k31T5yE3OZBZBQZDZDs'


if __name__ == '__main__':
    GraphApiUtil.access_token = my_token
    graph = facebook.GraphAPI(access_token=my_token, version='2.7')








