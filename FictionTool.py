#!/usr/bin/python3

import WebParser as wp
from optparse import OptionParser as op
import sys
import os
import errno
import MailDelegate
import Auth

downloadPath = "/home/jackzhao/Downloads/"

class FictionBot:
    
    url = None
    bookTitle = None
    path = None

    def __init__(self, bookTitle = None, url = None):
        if bookTitle:
            self.url, self.bookTitle = wp.searchBook(bookTitle)
            self.bookTitle.replace(' ', '')
            self.url = wp.rootUrl + self.url
        elif url:
            self.bookTitle = "untitled"
            self.url = url

    def setUrl(self, url):
        if 'html' in url:
            print('请使用目录链接')
            exit(1)
        self.url = url

    def updatePath(self):

        if self.bookTitle:
            self.path = downloadPath + self.bookTitle + '/'
        if not os.path.exists(os.path.dirname(self.path)):
            try:
                os.makedirs(os.path.dirname(self.path))
                print("Make directory: " + self.path)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

    def checkLog(self):
        try:
            f = open(self.path+'log.txt')
            f.seek(0)
            lastTimeLength = f.read()
        except IOError:
            print('no log file found, creating new one...')
            f = open(self.path+'log.txt','w')
            lastTimeLength = 0
            f.write(str(lastTimeLength))
        f.close()
        return int(lastTimeLength)

    def log(self, newdata):
        f = open(self.path+'log.txt','w')
        f.write(str(newdata))
        f.close()

        
    def download(self, lastNchapter = -1):
        if self.url is None:
            print("Error, no url loaded")
            exit(1)
        else:
            self.bookTitle = wp.getBookTitle(self.url)
            
        if 'html' in self.url:
            print('Menu URL error')
            exit(0)
        
        self.updatePath()

        chList = wp.getChapterList(self.url)
        currentLength = len(chList)

        if lastNchapter == -1:
            # 检查上次更新长度
            lastTimeLength = self.checkLog()
            # 检查结束
        else:
            lastTimeLength = int(currentLength) - int(lastNchapter) - 1

        if lastTimeLength > currentLength:
            print('Unexpected list length, check lastTimeLength')
            exit(1)
        elif lastTimeLength == currentLength:
            print(self.bookTitle + ' --> 未更新' + str(currentLength))
            exit(0)


        fileName = str(lastTimeLength + 1) + '-' + str(currentLength) + ' ' + self.bookTitle

        f = open(self.path + fileName + '.txt', 'a')

        for i in range(lastTimeLength, currentLength):
            if i == 0:
                f.write(self.bookTitle + '\n\n')
            f.write(wp.downloadFromPage(wp.rootUrl+chList[i]['href']) + '\n')
            print("\rDownloading " + self.bookTitle + ":" + str(int((i - lastTimeLength)*100.0/(currentLength-lastTimeLength - 1))) +' %', end = '', flush=True)
            #sys.stdout.flush()
        sys.stdout.write('\n\n 下载完成：' + self.bookTitle  + '\n\n')
        f.close()
        # 记录当前长度
        self.log(currentLength)
        return fileName + '.txt', self.path + fileName + '.txt'

def main():
    version_msg = "%prog Version 0.1 (initial build)"
    usage_msg = '''%prog [OPTIONS]
   A tool helps you download fictions from https://www.biquge.com.cn
   to local environment or send to designated email receiver.'''
    
    parser = op(version = version_msg, usage = usage_msg)
    parser.add_option("-d", action="store", dest="downloadBook",
                      help = "Search for a book and return the first result in the list.")
    parser.add_option("-n", action = "store", dest = "lastNchapter",
                      help = "Download the last N chapters")
    parser.add_option("-r", action = "store", dest = "receiver",
                      help = "Set receiver email address")
    parser.add_option("-u", "--url", action = "store", dest = "fictionURL",
                      help = "Set download URL")
    parser.add_option("-s", "--send", action = "store", dest = "send",
                      help = "Send local file to email")
    
    options, args = parser.parse_args(sys.argv[1:])

    bookName = options.downloadBook
    lastNchapter = options.lastNchapter
    receiver = options.receiver
    url = options.fictionURL
    send = options.send

    if bookName is None and url is None:
        print("At least one input required!")
        exit()
    elif bookName and url:
        print("Too many inputs")
        exit()

    if bookName:
        fictionBot = FictionBot(bookName)

    if url:
        fictionBot = FictionBot(url = url)

    if lastNchapter:
        book, localPath = fictionBot.download(lastNchapter)
    else:
        book, localPath = fictionBot.download()

    if send:
        MailDelegate.sendEmail(Auth.login, Auth.passwd, receiver, localPath, "text.txt")
    if receiver:
        MailDelegate.sendEmail(Auth.login, Auth.passwd, receiver, localPath, book)



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
