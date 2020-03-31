# -*- coding: utf-8 -*-
import urllib, random, webbrowser
# import pytagcloud
from datetime import datetime, timedelta
import os, sys
from konlpy import jvm
from konlpy.tag import Okt, Twitter
from collections import Counter
from bs4 import BeautifulSoup
import numpy
import jpype, simplejson, konlpy
from newspaper import Article
from selenium import webdriver
import re
import copy

print(u"""*******************************************************************************
Description: "네이버뉴스_크롤링.py"
folderPATH:  None
JAVA and JAVA_HOME CLASS PATH Required 
Date Created: 10/02/2019
Copyright (c) 2019 Won-Jin Jang All rights reserved.
*******************************************************************************""")

# Python 2.x, Anaconda 5.x, pip -pytagcloud, konlpy, collections, bs4, pygame, simplejson, Windowinstall - javajdk

def parsingNaverNews(Date, SearchingData):
    url = "https://search.naver.com/search.naver?where=news&query=" + SearchingData + "&sm=tab_opt&sort=0&photo=1&field=0&reporter_article=&pd=3&ds=" + Date + "&de=" + Date

    nextpage = 0
    while nextpage == 0:

        html0 = urllib.urlopen(url)
        nextpage = 0
        bs_obj = BeautifulSoup(html0, "html.parser")

        ul = bs_obj.find("ul", {"class": "type01"})

        lis = ul.findAll("li")

        for li in lis:
            dt_tag = li.find("dt")
            dd_tag = li.findAll("dd")

            # 뉴스 title parsing
            try:
                name = dt_tag.a['title']
            except AttributeError:
                continue

            # 뉴스 내용 parsing
            try:
                description = dd_tag[1].get_text()
            except IndexError:
                pass

            # 언론사 이름 parsing
            try:
                aname = dd_tag[0].get_text().split()[0]
            except IndexError:
                pass
            news_data = {'Title':name, 'description' : description, "article":aname}
            newslist.append(news_data)

        # Get Next Page Url
        paging = bs_obj.findAll("div","paging")
        try:
            for k in paging:
                paging2 = k.find('a', 'next')
            url = "http:" + paging2['href']
        except TypeError:

            nextpage = 1
    return newslist

def get_tags(text, ntags = 9999):
    spliter = Okt()
    nouns = spliter.nouns(text)
    count = Counter(nouns)
    return_list = []
    for n, c in count.most_common(ntags):
        temp = {'tag':n, 'count':c}
        return_list.append(temp)
    return return_list

def listtotext(list):
    text = ""
    for k in list:
        for i in "Title", "description":
            text += " " + k[i]
    return text

def counter_to_text(text, BDate):
    # 분석할 파일
    noun_count = 500
    # 최대 많은 빈도수 부터 500개 명사 추출
    output_file_name = str(BDate.strftime("%Y%m.txt"))
    # 분석할 파일을 open
    tags = get_tags(text, noun_count) # get_tags 함수 실행
    open_output_file = open(os.getcwd() + "\\" + output_file_name, 'w')
    # 결과로 쓰일 count.txt 열기
    for tag in tags:
        noun = tag['tag'].encode('utf-8')
        count = tag['count']
        open_output_file.write('{} {}\n'.format(noun, count))
    # 결과 저장
    open_output_file.close()

def get_tags_RandomColor(text, ntags=50, multiplier=3):

    spliter = Twitter()
    nouns = spliter.nouns(text)
    count = Counter(nouns)
    return [{ 'color': color(), 'tag': n, 'size': (c*multiplier)/2 }\
                for n, c in count.most_common(ntags)]

def parsingbywebdriver(url):
    driver.get(url)
    driver.find_element_by_xpath('// *[ @ id = "news_popup"]').click()
    driver.implicitly_wait(0.5)
    driver.find_element_by_id("ca_p1").click()
    # driver.find_element_by_id("ca_p2").click()
    # driver.find_element_by_id("ca_p4").click()
    # driver.find_element_by_id("ca_p6").click()
    driver.implicitly_wait(0.5)
    driver.find_element_by_xpath('//*[@id="_nx_option_media"]/div[2]/div[3]/button[1]').click()
    driver.implicitly_wait(0.5)
    return driver

def cleantxt(txt):
    text = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', txt)
    return text

if __name__ == "__main__":
    if not os.path.isdir('Results'):
        os.mkdir('Results')

    SearchingData = input("Tags : ")
    ChangeDay = timedelta(days=1)
    startDate = input("StartDate(YYYY.MM.DD) : ")
    endDate = input("EndDate(YYYY.MM.DD) : ")
    A = startDate.split(".")
    B = endDate.split(".")
    Startdate = datetime(int(A[0]), int(A[1]), int(A[2]))
    Next = copy.deepcopy(Startdate)

    while Startdate.month == Next.month:
        Next = Next + ChangeDay
    Enddate = datetime(int(B[0]),int(B[1]),int(B[2]))
    driver = webdriver.Chrome(r'.\chromedriver.exe')
    driver.implicitly_wait(1)

    while Startdate <= Enddate:
        Sdate = Startdate.strftime("%Y.%m.%d")
        Ndate = Next.strftime("%Y.%m.%d")
        url = "https://search.naver.com/search.naver?where=news&query=" + str(SearchingData) + "&sm=tab_opt&sort=0&photo=1&field=0&reporter_article=&pd=3&ds=" + Sdate + "&de=" + Ndate
        driver = parsingbywebdriver(url)
        endup = 0
        txterr = 0
        while endup < 1:
            html = driver.page_source
            bs_obj = BeautifulSoup(html, "html.parser")
            try:
                ul = bs_obj.find("ul", {"class": "type01"})
                lis = ul.findAll("li")
                for li in lis:
                    dt_tag = li.find("dt")
                    dd_tag = li.findAll("dd")
                    # 뉴스 title parsing
                    try:
                        name = dt_tag.a['title']
                    except AttributeError:
                        # print("소제목 Detect")
                        continue
                    # 뉴스 내용 parsing
                    try:
                        link = dt_tag.a['href']
                        paper = Article(link, language = 'ko')
                        paper.download()
                        paper.parse()
                        description = paper.text
                    except:
                        print("뉴스내용 Err" + name)
                        txterr = 1
                        pass
                    # 언론사 이름 parsing
                    try:
                        aname = dd_tag[0].get_text().split()[0]
                    except IndexError:
                        print("뉴스언론사 Err")
                        pass
                    try:
                        print(name)
                        with open(os.getcwd()+"\\Results\\"+Startdate.strftime("%Y%m")+"_"+cleantxt(name)+".txt", 'w', encoding="utf-8") as Fopen:
                            if txterr != 1:
                                Fopen.write(description + "\n")
                                Fopen.write("*" + aname + "*")
                            txterr = 0
                    except:
                        print("Encode,Decode Err")
                try:
                    driver.find_element_by_class_name("next").click()
                except:
                    # print("data collecting Done in:)" + Startdate.strftime("%Y.%m"))
                    endup = 1
            except:
                print("No data in " + Startdate.strftime("%Y.%m"))
                endup = 1
        Startdate = copy.deepcopy(Next)
        while Startdate.month == Next.month:
            Next = Next + ChangeDay