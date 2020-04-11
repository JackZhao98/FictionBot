#! /usr/bin/python3

import re
import requests

rootUrl = 'https://www.biquge.com.cn'

def getPageSource(url):
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
    html = requests.get(url, headers = headers)
    return html

def searchBook(bookTitle):
    searchUrl = rootUrl + '/search.php?q=' + bookTitle
    html = getPageSource(searchUrl)
    listReg = re.compile(r'<a cpos="title".*?blank">')
    firstResult = re.findall(listReg, html.text)
    if len(firstResult) <= 0:
        print("未找到:" + bookTitle)
        exit(0)
    else:
        firstResult = firstResult[0]

    hrefReg = re.compile(r'href=\"(.*?)\"')
    titleReg = re.compile(r'title=\"(.*?)\"')
    urlExt = re.findall(hrefReg, firstResult)[0];
    bookTitle = re.findall(titleReg, firstResult)[0];
    #print(urlExt + ' ' + bookTitle)
    return urlExt, bookTitle

def getBookTitle(menuUrl):
    html = getPageSource(menuUrl)
    titleReg = re.compile(r'<h1>(.*?)</h1>')
    title = re.findall(titleReg, html.text)
    if len(title) > 0:
        return title[0]
    else:
        print('Unexpected error while extracting the title')
        exit(1)

def getChapterList(menuUrl):
    html = getPageSource(menuUrl)
    listReg = re.compile(r'<dd>(.*?)</dd>')
    chapterList = re.findall(listReg, html.text)
    htmlReg = re.compile(r'<a href="(.*?)"')
    titleReg = re.compile(r'>(.*?)</a>')
    data = []
    for item in chapterList:
        url = re.findall(htmlReg, item)[0]
        title = re.findall(titleReg, item)[0]
        if title[0] == ' ':
            title = title[1:]
        data.append({'href':url, 'title':title})
    return data

def downloadFromPage(pageUrl):
    html = getPageSource(pageUrl)
    titleReg = re.compile(r'<h1>(.*?)</h1>')
    contentReg = re.compile(r'<div id="content">(.*?)</div>')
    cleanReg = re.compile(r'&nbsp;')

    content = re.findall(contentReg, html.text)[0]
    content = re.sub(cleanReg, " ", content)
    content = content.replace('<br>', '\n')
    title   = re.findall(titleReg, html.text)[0]

    return title + "\n\n" + content + '\n\n'
