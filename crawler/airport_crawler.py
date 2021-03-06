# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 20:59:11 2020

@author: liming
"""

from bs4 import BeautifulSoup
import xlwt
import datetime
import requests
import json

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}

headers2 = {
    'X-Requested-With': 'XMLHttpRequest',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}

base_url = 'https://www.5688.com.cn'
        
def set_style(name, height, bold = False):
    style = xlwt.XFStyle() #初始化样式
    font = xlwt.Font() #为样式创建字体
    font.name = name
    font.bold = False
    font.color_index = 4
    font.height = height
    style.font = font
    return style

class Crawler:
    def __init__(self):
        self.session = requests.session()
        self.session.headers.update(headers)
        self.crawl_timestamp = int()
        #self.airport_list = []
        #创建工作簿
        self.workbook = xlwt.Workbook(encoding='utf-8')
        #创建sheet
        self.data_sheet = self.workbook.add_sheet('airport')
        self.index = 0
        self.default_tyle = set_style('Times New Roman',220, True)
        
    def get_airport_detail_urls(self,url):
        try:
            response = self.session.get(url = url)
            if response.status_code == 200:
                text = str(response.content,encoding='utf-8')
                soup = BeautifulSoup(text, 'lxml')
                css = 'html body div.tool_model_box div.left div.port_list div.category ul li'
                return list(map(lambda x: (x.a['href'],x.a.string), soup.select(css)))
        except requests.exceptions.ChunkedEncodingError:
            print('error')
            
    def get_next_detail(self,content,country):
        try:
            soup = BeautifulSoup(content,'lxml')
            list1 = list(map(lambda x: x,soup.select('tr')))
            if list1[0].select('td')[0].text == '未查询到数据':
                return
            #先爬取当前页面
            for item in list1:
                list2 = list(map(lambda x: x.a.text.replace('海关',''),item.select('td')))
                #每一列的内容(i)
                for x,item in enumerate(list2):
                    #下标(x)，单元元素(item)
                    self.data_sheet.write(self.index, x, item, self.default_tyle)
                self.index += 1
        except requests.exceptions.ChunkedEncodingError:
            print('error')
            
    def get_airport_detail(self,url,country):
        try:
            response = self.session.get(url = url)
            if response.status_code == 200:
                text = str(response.content,encoding = 'utf-8')
                soup = BeautifulSoup(text,'lxml')
                css = 'html body div.tool_model_box div.left div.port_list tbody.tbody tr'
                list1 = list(map(lambda x: x,soup.select(css)))
                if list1[0].select('td')[0].text == '未查询到数据':
                    return
                #先爬取当前页面
                for item in list1:
                    list2 = list(map(lambda x: x.a.text.replace('海关',''),item.select('td')))
                    #每一列的内容(i)
                    for x,item in enumerate(list2):
                        #下标(x)，单元元素(item)
                        self.data_sheet.write(self.index, x, item, self.default_tyle)
                    self.index += 1
                
                page = soup.select_one('html body div.tool_model_box div.left div.page.airport_search')
                #如果有分页
                if page and page.text != '':
                    page_list = list(map(lambda x:x,page.select('a')))
                    last_page = page_list[-1]
                    if last_page and last_page.text != '末页':
                        last_page = page_list[-2]
                    total_page = last_page['data-ci-pagination-page']
                    page_url = last_page['rel']
                    page_base_url = page_url[0].replace(total_page,'')
                    
                    for index in range(1,int(total_page)):
                        next_page_url = base_url + page_base_url + str(index + 1)
                        self.session.headers.update(headers2)
                        next_page_resp = self.session.get(url = next_page_url)
                        if next_page_resp.status_code == 200:
                            next_page_content = str(next_page_resp.content,encoding = 'utf-8')
                            #print(json.loads(next_page_content)['list'])
                            self.get_next_detail(json.loads(next_page_content)['list'],country)
                #如果没有分页
                else:
                    return
                    '''
                    for item in list1:
                        list2 = list(map(lambda x: x.a.text.replace('海关',''),item.select('td')))
                        #airport =  Airport(list2[0],list2[1],list2[2],list2[3])
                        #self.airport_list.append(airport)
                        #每一列的内容(i)
                        for x,item in enumerate(list2):
                            #下标(x)，单元元素(item)
                            print(item)
                            self.data_sheet.write(self.index, x, item, self.default_tyle)
                        self.index += 1
                    '''
                        
        except requests.exceptions.ChunkedEncodingError:
            print('error')
                
        
    def run(self):
        self.crawl_timestamp = int(datetime.datetime.timestamp(datetime.datetime.now())*1000)
        detail_urls = self.get_airport_detail_urls(base_url + '/airport')
        for detail in detail_urls:
            self.get_airport_detail(base_url + detail[0],detail[1])  
        #保存文件
        self.workbook.save('airport.xls')

class Airport:
    def __init__(self,code_iata,name_en,name_cn,country_cn):
        self.code_iata = code_iata
        self.name_en = name_en
        self.name_cn = name_cn
        self.country_cn = country_cn
            
crawler = Crawler()
crawler.run()
        


