'''
author: xiche
create at: 09/01/2018
description:
    Spider for 51 Job
Change log:
Date        Author      Version    Description
09/01/2018  xiche       1.0        Set up
'''
import requests
import os
import codecs
import re
import time
import jieba.analyse

from urllib.parse import unquote
from urllib.parse import quote
from contextlib import closing
from bs4 import BeautifulSoup
from pyecharts import WordCloud
from pyecharts import Bar
from pyecharts import Grid
from collections import Counter


from lib.spider_utils import Spider
class JobInfo(object):
    job_title = ''
    company = ''
    location = ''
    __salary = ''
    __salary_with_units = ''
    salary_min = 9999
    date_release = ''
    def __str__(self):
        return ','.join([self.job_title, self.company, self.location, self.salary, self.date_release])
    
    @property
    def salary(self):
        return self.__salary
       
    @salary.setter
    def salary(self, salary):
    # categories=['千/月', '万/月', '万/年']
        if not salary or salary == '':
            self.__salary =  'UNKNOWN'
            return
        matchObj = re.match( '([0-9]{1,}.*[0-9]*)-([0-9]{1,}.*[0-9]*)(\S/\S)', salary, re.M|re.I)
        
        if matchObj:
           salary_min = matchObj.group(1)
           salary_max = matchObj.group(2)
           salary_units = matchObj.group(3)
        categories = {
            "千/月":lambda x:round(x, 0),
            "万/月":lambda x:round(x*10, 0),
            "万/年":lambda x:round(x/12*10, 0)
        }
        # print(salary_min, salary_max, salary_units,'$$$$$$$$$$$$$$$$')
        # print(salary_min, salary_units)
        salary_min = categories[salary_units](float(salary_min))
        salary_max = categories[salary_units](float(salary_max))
        salary_units = 'K/M'
        self.salary_min = float(salary_min)
        self.__salary_with_units =  "{:.0f}-{:.0f}{}".format(salary_min, salary_max, salary_units)
        self.__salary = "{:.0f}-{:.0f}".format(salary_min, salary_max)

class Spider51Job(Spider):
    start       = 0
    page_total  = 1
    list_job_info = []
    def __init__(self, page=2):
        self.url_request = 'https://search.51job.com/list/080200,000000,0000,00,9,99,{keyword},2,{page_num}.html?'\
                            'lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99'\
                            '&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9'\
                            '&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
        self.page = page

    def parse_html(self, html=None):
        html = html if html else self.html
        soup = BeautifulSoup(html, "html.parser")
        list_job_soup = soup.find('div',class_='dw_table')#('div', attrs={'class': 'dw_table'})
        # print(list_job_soup)
        # get job info list
        for job_div in list_job_soup.find_all('div', class_='el'): #list_job_soup.find_all('div', attrs={'class': 'el'})
            job_info = JobInfo()
            # print(job_div.select('div[class="el"]'))
            if not job_div.select('p'):
                continue
            if job_div.find('p',class_='t1'):
                job_info.job_title = job_div.find('p',class_='t1').find('span').find('a').getText().strip()

            if job_div.find('span',class_='t2').find('a'):
                job_info.company = job_div.find('span',class_='t2').find('a').getText().strip()
                if(not '道富' in job_info.company): continue

            if job_div.find('span',class_='t3'):
                job_info.location = job_div.find('span',class_='t3').getText().strip()

            if job_div.find('span',class_='t4'):
                job_info.salary = job_div.find('span',class_='t4').getText().strip()

            if job_div.find('span',class_='t5'):
                job_info.date_release = job_div.find('span',class_='t5').getText().strip()   
            self.list_job_info.append(job_info)

        # get total page
        page_info = list_job_soup.find(class_='p_in').find('span', class_='td').getText().strip()
        self.page_total = int(re.sub(r'\D', "", page_info))
    
    def generate_chart_bar(self, item_name, item_name_list, item_num_list):
        subtitle = "Salary Range RMB(K/Month)"
        bar = Bar(item_name,page_title = item_name,title_text_size=30,title_pos='center',\
            subtitle = subtitle,subtitle_text_size = 25)
        
        bar.add("", item_name_list, item_num_list,title_pos='center', xaxis_interval=0,xaxis_rotate=27,\
            xaxis_label_textsize = 20,yaxis_label_textsize = 20,yaxis_name_pos='end',yaxis_pos = "%50")
        bar.show_config()

        grid = Grid(width=1300,height= 800)
        grid.add(bar,grid_top = "13%",grid_bottom = "23%",grid_left = "15%",grid_right = "15%")
        out_file_name = './'+item_name+'.html'
        grid.render(out_file_name)

    def generate_word_cloud(self, item_name,item_name_list,item_num_list,word_size_range):

        wordcloud = WordCloud(width=1400,height= 900)
        
        wordcloud.add("", item_name_list, item_num_list,word_size_range=word_size_range,shape='pentagon')
        out_file_name = './'+item_name+'.html'
        wordcloud.render(out_file_name)

    def counter2list(self, _counter):
        name_list = []
        num_list = []
        for item in _counter:
            name_list.append(item[0])
            num_list.append(item[1]) 
        return name_list,num_list

    def analyse_job_info(self):
        self.list_job_info.sort(key=lambda x:x.salary_min,reverse=False)
        
        list_salary_all = [x.salary for x in self.list_job_info]
        list_salary_unique = []
        for salary in list_salary_all:
            if salary not in list_salary_unique:
                list_salary_unique.append(salary)
        # print(list_salary_all)
        # set_salary = set(list_salary_all)
        # list_salary_unique = [x for x in set_salary]
        list_salary_count = []
        for salary in list_salary_unique:
            list_salary_count.append(list_salary_all.count(salary))

        # print(list_salary_unique)
        # print(list_salary_count)
        
        self.generate_chart_bar('StateStreet Hot Job on 51job - Salary',list_salary_unique, list_salary_count)
        job_title_counter = Counter()
        for job_info in self.list_job_info:
            tag_list = jieba.analyse.extract_tags(job_info.job_title)
            for tag in tag_list:
                job_title_counter[tag] += 1

        name_list,num_list = self.counter2list(job_title_counter.most_common(200))

        self.generate_word_cloud('StateStreet Hot Job on 51job - Keywork',name_list,num_list,[20,100])

    def start_spider(self):
        str_search  = '道富'
        page_num    = 1
        # str_search = quote(str_search, 'utf-8')
        # str_search = quote(str_search, 'utf-8')
        while(page_num <= self.page_total):
            
            info_01 = 'collect data in page {}...'.format(page_num)
            info_02 = 'collect data in page {}/{}...'.format(page_num,self.page_total)
            if(page_num == 1):
                print(info_01)
            else:
                print(info_02)

            self.url_request =self.url_request.format(keyword = str_search, page_num = page_num)
            self.download_page()
            # self.save_page_to_file()
            # self.get_page_from_saved_file()
            self.parse_html()
            page_num += 1
            print('wait 1 second...' )
            time.sleep(1)
            
        self.analyse_job_info()
        # self.list_job_info.sort(key=lambda x:x.job_title,reverse=False)
        # for job_info in self.list_job_info:
        #     print(job_info)
        

if __name__ == '__main__':
    spider_51job = Spider51Job()
    spider_51job.start_spider()
    # line = "0.8-1.5万/月"
    # matchObj = re.match( '([0-9]{1,}[.][0-9]*)-([0-9]{1,}[.][0-9]*)(\S/\S)', line, re.M|re.I)
    # if matchObj:
    #     print ("matchObj.group() : ", matchObj.group())
    #     print ("matchObj.group(1) : ", matchObj.group(1))
    #     print ("matchObj.group(2) : ", matchObj.group(2))
