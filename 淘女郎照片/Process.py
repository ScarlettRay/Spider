# coding:utf8

import requests
from bs4 import BeautifulSoup
import os
from contextlib import closing
from requests import Request, Session

# 首页的url
indexUrl = 'https://mm.taobao.com/tstar/search/tstar_model.do?_input_charset=utf-8'
#用户主页
picUrl='https://mm.taobao.com/self/aiShow.htm'
#照片储存位置
dirPath='E:\淘女郎'
#搜索条件（欧美 韩版 日系 英伦 OL风 学院 淑女 性感 复古 街头 休闲 民族 甜美 运动 可爱 大码 中老年 美妆）
searchStyle="性感"
#获取多少页的用户
pageNum=2

# 爬去流程
def Process():
    session = Session()
    #获取淘女郎uid和各种信息·_·
    for curPage in range(1,pageNum):
        resp=passMes("POST",indexUrl,session,data={'currentPage':curPage,'pageSize':'100','searchStyle':searchStyle})
        grilList=resp.json()['data']['searchDOList']
        for index in range(len(grilList)):
            grilMes=grilList[index]
            # 获取用户主页
            resp=passMes("GET",picUrl,session,params={'userId':grilMes['userId']})
            # 获取图片地址件
            picurls=getPicURL(resp.text,str(grilMes['userId']))
            # 创建文夹
            dirpath=mkDir(grilMes['realName'],grilMes['city'],grilMes['height'],grilMes['weight'],str(grilMes['totalFavorNum']))
            # 储存图片（主页图片和一张头像）
            writePic(dirpath,session,url=grilMes["avatarUrl"])
            writePic(dirpath,session,urls=picurls)
            # 写入个人介绍
            with closing(open(dirpath+"\\她的信息~.txt","w",encoding="utf8")) as fp:
                getGrilMes(resp.text,fp)

#获取联系方式
def getGrilMes(text,file):
    soup=BeautifulSoup(text,"html.parser")
    div=soup.find_all("div",class_="mm-aixiu-content")[0]
    for p in div.stripped_strings:
        file.write(p+"\n")

# 写入图片
def writePic(dirpath, session,url=None, urls=None):
    import time
    index = 0
    if url == None:
        for url in urls:
            index = index + 1
            r = passMes("GET", "https:" + url,session)
            with closing(open(dirpath + "\\" + str(index) + ".jpg", "wb")) as fp:
                fp.write(r.content)
    else:
        r = passMes("GET", "https:" + url,session)
        with closing(open(dirpath + "\\" + str(time.time()) + ".jpg", "wb")) as fp:
            fp.write(r.content)

#在指定文件夹下创建目录
def mkDir(name,city,height,weight,totalFavorNum):
    import os
    mes=[name,city,height,weight,totalFavorNum]
    print(mes)
    dirname=" ".join(mes)
    path=dirPath+"\\"+dirname
    os.mkdir(path)
    return path


#获取图片地址
def getPicURL(text,userId):
    import re
    matches=re.findall(r'//img\..+?\.(?:jpg|png)',text)
    print(len(matches))
    temp=sorted(set(matches), key=matches.index)
    picUrls=[]
    for url in temp:
        if userId in url:
            picUrls.append(url)
    return picUrls


def passMes(method, url,session=None,data=None,params=None):
    if session==None:
        session=Session()
    # 伪装成Chrome
    headers = {"User-Agent":
                   "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"}
    req = Request(method, url, data=data, params=params,headers=headers)
    prepare=session.prepare_request(req)
    try:
        resp=session.send(prepare,timeout=10)
    except:
        #try again
        resp = session.send(prepare, timeout=10)
        return resp
    return resp


# Gril类，存储信息
# class Gril():
#     def __init__(self):


'''Url管理类
'''


class UrlsManager():
    # url模式，url元组
    def __init__(self, urlpattern):
        self.pos = -1
        self.urlpattern = urlpattern
        # 是否为元组
        self.urlTypeflag = True if isinstance(self.urlpattern, tuple) else False
        if self.urlTypeflag:
            self.length = len(self.urlpattern)

    # 返回一个url
    def getOneUrl(self):
        if self.urlTypeflag:
            self.pos = self.pos + 1
            if self.pos < self.length:
                return self.urlpattern[self.pos]
        else:
            return self.urlpattern

    # 构造Uri,返回一个完整路径
    def buildURI(url, path):
        return ''.join([url, path]) if url.endwidth("/") else "/".join([url, path])

if __name__ == "__main__":
    import argparse
    parse=argparse.ArgumentParser(description='从淘女郎中爬去妹子的图片和个人信息！')
    parse.add_argument("-s","--searchStyle",default=None,
                       help="需要那种风格的妹子，待选参数（欧美 韩版 日系 英伦 OL风 学院 淑女 性感 复古 街头 休闲 民族 甜美 运动 可爱 大码 中老年 美妆")
    parse.add_argument("--dir",default="E:\淘女郎",
                       help="保存图片的目录")
    args = parse.parse_args()
    if args.searchStyle:
        searchStyle=args.searchStyle
    if args.dir:
        dirPath=args.dir
    Process()



