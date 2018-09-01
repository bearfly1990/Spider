'''
author: xiche
create at: 09/01/2018
description:
    Spider Utils
Change log:
Date        Author      Version    Description
09/01/2018  xiche       0.0.1      Set up
'''
import requests
import os
import re
import codecs
from contextlib import closing
from bs4 import BeautifulSoup
from abc import abstractmethod, ABC

class Spider(ABC):
    url_request = ''
    html = ''
    HEADER_BROWER = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
            'Chrome/63.0.3239.132 Safari/537.36'}

    def download_page(self):
        data_req = requests.get(self.url_request, headers=self.HEADER_BROWER)
        html = 'aa'
        # print(requests.utils.get_encoding_from_headers(data_req.headers))
        # data_encoding_real = data_req.encoding
        data_encoding_appr = data_req.apparent_encoding
        html = data_req.content.decode(data_encoding_appr).encode('utf-8').decode('utf-8')
        # print(data_req.apparent_encoding)
        #data_req.text.encode(data_req.encoding).decode('gbk')
        # print(html)
        self.html = html
        return html

    def save_page_to_file(self):
        with codecs.open('saved.html', 'w', encoding='utf-8') as fp:
            fp.write(self.html)

    def get_page_from_saved_file(self):
        with open('saved.html', 'r', encoding='utf-8') as fp:
            self.html = fp.read()

    @abstractmethod
    def parse_html(self, html):
       pass

    @abstractmethod
    def start_spider(self):
        pass

    def getPic(self, data):
        pic_list = re.findall(r'src="http.+?.jpg"', data)
        return pic_list

    def download_pic(self, url, name, folder = 'imgs/'):
        rootPath = folder
        if not os.path.exists(rootPath):
            os.makedirs(rootPath)
        response = requests.get(url, stream=True)
        pic_type = '.' + url.split('.')[-1]
        with closing(requests.get(url, stream=True)) as responses:
            with open(rootPath + name + pic_type, 'wb') as file:
                for data in response.iter_content(128):
                    file.write(data)