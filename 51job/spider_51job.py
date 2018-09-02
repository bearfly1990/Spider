'''
author: xiche
create at: 09/01/2018
description:
    Spider for 51 Job
Change log:
Date        Author      Version     Description
09/01/2018  xiche       1.0         Set up

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
    salary_with_units = ''
    salary_min = 9999999
    salary_avg = 9999999
    __date_release = ''
    def __str__(self):
        return ','.join([self.job_title, self.company, self.location, self.salary, self.date_release])
    
    @property
    def salary(self):
        return self.__salary

    @salary.setter
    def salary(self, salary):
        # print(salary)
        if not salary or salary == '':
            self.__salary =  'UNKNOWN'
            return
        if "元/天" in salary:
            matchObj = re.match( '(\d+)(\S/\S)', salary, re.M|re.I)
            if matchObj:
                salary_min = matchObj.group(1)
                salary_max = matchObj.group(1)
                salary_units = matchObj.group(2)
        else:
            matchObj = re.match( '([0-9]{1,}.*[0-9]*)-([0-9]{1,}.*[0-9]*)(\S/\S)', salary, re.M|re.I)
            if matchObj:
                salary_min = matchObj.group(1)
                salary_max = matchObj.group(2)
                salary_units = matchObj.group(3)
        categories = {
            "元/天":lambda x:round(x*30, 0),
            "千/月":lambda x:round(x, 0),
            "万/月":lambda x:round(x*10, 0),
            "万/年":lambda x:round(x/12*10, 0)
        }
        # print(salary_min, salary_max, salary_units,'$$$$$$$$$$$$$$$$')
        # print(salary_min, salary_units)
        salary_min = categories[salary_units](float(salary_min))
        salary_max = categories[salary_units](float(salary_max))
        salary_avg = (salary_min+salary_max)/2
        salary_units = 'K'
        self.salary_min = float(salary_min)
        self.salary_avg = salary_avg
        # self.__salary_with_units =  "{:.0f}-{:.0f}{}".format(salary_min, salary_max, salary_units)
        # self.__salary = "{:.0f}-{:.0f}".format(salary_min, salary_max)
        self.salary_with_units = "{:.0f}{}".format(salary_avg, salary_units)
        self.__salary = "{:.0f}".format(salary_avg)

class Spider51Job(Spider):
    start       = 0
    page_total  = 1
    list_job_info = []
    str_search  = '道富'
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
            # print(job_info)
            # print(job_div.select('p'))
            if not job_div.select('p'):
                continue
            if job_div.find('p',class_='t1'):
                job_info.job_title = job_div.find('p',class_='t1').find('span').find('a').getText().strip()

            if job_div.find('span',class_='t2').find('a'):
                job_info.company = job_div.find('span',class_='t2').find('a').getText().strip()
                if(not self.str_search in job_info.company): continue
                       
            if job_div.find('span',class_='t3'):
                job_info.location = job_div.find('span',class_='t3').getText().strip()

            if job_div.find('span',class_='t4'):
                job_info.salary = job_div.find('span',class_='t4').getText().strip()

            if job_div.find('span',class_='t5'):
                job_info.date_release = job_div.find('span',class_='t5').getText().strip()   
            self.list_job_info.append(job_info)
            # print(job_info)

        # get total page
        page_info = list_job_soup.find(class_='p_in').find('span', class_='td').getText().strip()
        self.page_total = int(re.sub(r'\D', "", page_info))
    
    def generate_chart_bar(self, item_name, sub_title, item_name_list, item_num_list):
        bar = Bar(item_name,page_title = item_name,title_text_size=30,title_pos='center',\
            subtitle = sub_title,subtitle_text_size = 25)
        
        bar.add("", item_name_list, item_num_list,title_pos='center', xaxis_interval=0,xaxis_rotate=27,\
            xaxis_label_textsize = 20,yaxis_label_textsize = 20,yaxis_name_pos='end',yaxis_pos = "%50")
        bar.show_config()

        grid = Grid(width=1300,height= 800)
        grid.add(bar,grid_top = "13%",grid_bottom = "23%",grid_left = "15%",grid_right = "15%")
        out_file_name = './analysis_result/'+item_name+'.html'
        grid.render(out_file_name)

    def generate_word_cloud(self, item_name,item_name_list,item_num_list,word_size_range):

        wordcloud = WordCloud(width=1400,height= 900)
        
        wordcloud.add("", item_name_list, item_num_list,word_size_range=word_size_range,shape='pentagon')
        out_file_name = './analysis_result/'+item_name+'.html'
        wordcloud.render(out_file_name)

    def counter2list(self, _counter):
        name_list = []
        num_list = []
        for item in _counter:
            name_list.append(item[0])
            num_list.append(item[1]) 
        return name_list,num_list

    def analyse_job_info(self):
        self.list_job_info.sort(key=lambda x:x.salary_avg,reverse=False)
        
        list_salary_all = [x.salary_with_units for x in self.list_job_info]
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
        self.generate_chart_bar('Hot Job on 51job - Salary [{}]'.format(self.str_search), "Salary Range RMB(K/Month)", list_salary_unique, list_salary_count)

        list_date_release = [x.date_release[:2] for x in self.list_job_info]
        list_date_release_unique = []
        for date_release in list_date_release:
            if date_release not in list_date_release_unique:
                list_date_release_unique.append(date_release)

        list_date_release_count = []
        for date_release in list_date_release_unique:
            list_date_release_count.append(list_date_release.count(date_release))
        # time_array = time.strptime(date_release, '%m-%d')
        # time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
        # self.date_release = time.strftime("%m", time_array)

        self.generate_chart_bar('Hot Job on 51job - JobReleasedCount [{}]'.format(self.str_search),"Numbers of released jobs at recent month",list_date_release_unique, list_date_release_count)

        job_title_counter = Counter()
        for job_info in self.list_job_info:
            tag_list = jieba.analyse.extract_tags(job_info.job_title)
            for tag in tag_list:
                job_title_counter[tag] += 1

        name_list,num_list = self.counter2list(job_title_counter.most_common(200))

        self.generate_word_cloud('Hot Job on 51job - Keywork [{}]'.format(self.str_search),name_list,num_list,[20,100])

        list_job_title = [x.job_title for x in self.list_job_info]

        num_list = [5 for i in range(1,len(list_job_title)+1)]
        self.generate_word_cloud('Hot Job on 51job - JobTitle [{}]'.format(self.str_search),list_job_title,num_list,[18,18])

    def start_spider(self):
       
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

            self.url_request =self.url_request.format(keyword = self.str_search, page_num = page_num)
            self.download_page()
            # self.save_page_to_file()
            # self.get_page_from_saved_file()
            self.parse_html()
            page_num += 1
            # print('wait 1 second...' )
            time.sleep(1)
            
        self.analyse_job_info()
        # self.list_job_info.sort(key=lambda x:x.job_title,reverse=False)
        # for job_info in self.list_job_info:
        #     print(job_info)
        

if __name__ == '__main__':
    spider_51job = Spider51Job()
    spider_51job.str_search = '恒生电子'
    spider_51job.start_spider()
    # line = "0.8-1.5万/月"
    # matchObj = re.match( '([0-9]{1,}[.][0-9]*)-([0-9]{1,}[.][0-9]*)(\S/\S)', line, re.M|re.I)
    # if matchObj:
    #     print ("matchObj.group() : ", matchObj.group())
    #     print ("matchObj.group(1) : ", matchObj.group(1))
    #     print ("matchObj.group(2) : ", matchObj.group(2))
