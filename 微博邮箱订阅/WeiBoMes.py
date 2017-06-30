# coding:utf8

"""用于订阅指定微博用户的微博状态,
    如有微博更新，向指定邮箱发送一封邮件"""
import smtplib
import requests
from email.mime.text import MIMEText
from email.utils import formataddr
from bs4 import BeautifulSoup
from threading import Timer
import time

style = '<style>body,blockquote,code,dd,div,dl,dt,fieldset,form,h1,h2,h3,h4,h5,h6,input,legend,li,ol,p,pre,td,textarea,th,ul{margin:0;padding:0}.W_btn_b,i{display:none}ul{text-decoration:none;list-style:none;padding:0}a{text-decoration:none;color:#eb7350}img{border:0}div{margin:0;padding:0;display:block}.SW_fun .S_func1,.S_txt1,.W_btn_b,.W_input:focus,body,legend{color:#333;text-decoration:none}.WB_face{position:relative;float:left}.S_txt2,.W_btn_b_disable,.W_btn_b_disable:hover,.W_input{color:grey;text-decoration:none}.WB_cardwrap{display:inline-block;letter-spacing:normal;word-spacing:normal;vertical-align:top;font-size:12px;margin:45px}.WB_face img{width:50px;height:50px}.face{width:50px;height:50px}.W_face_radius{border-radius:50%}.W_f14{font-size:14px}.W_fb{font-weight:700}.WB_feed_v3 .WB_info{margin-bottom:7px}.WB_info{margin:0 0 3px;padding:5px 0 0}.WB_detail{margin-left:60px}.WB_expand .WB_media_wrap{margin-top:6px;margin-bottom:8px}.WB_feed_expand .W_arrow_bor{display:none}.WB_feed_expand .W_arrow_bor{height:10px;overflow:hidden}.WB_media_wrap{margin:2px 0 8px -10px}.WB_media_wrap .media_box{font-size:0}.WB_media_wrap .media_box{float:left;margin:0 0 0 10px}.WB_media_a_mn{width:456px;margin:-4px 0 0 -4px}.WB_media_a_m9{width:342px}.WB_media_a_mn li{width:110px;height:110px;margin:4px 0 0 4px}.WB_media_a li{position:relative}.WB_media_a li:after{content:'';position:absolute;left:0;top:0;right:0;bottom:0;border:1px solid rgba(0,0,0,.05)}.S_bg1{background-color:#f2f2f5}.WB_expand{margin:5px -20px -4px -80px;padding:4px 20px 1px 80px}.WB_expand_media_box{margin:0 -20px 0 -80px}.WB_expand .WB_text{margin-top:-3px;margin-bottom:4px;line-height:21px}.WB_media_a_mn li{float:left;width:80px;height:80px;margin:6px 0 0 6px;overflow:hidden}.WB_media_a_mn li{width:110px;height:110px;margin:4px 0 0 4px}.WB_func .WB_handle ul{margin-right:-9px;overflow:visible}.WB_func .WB_handle li{float:right;margin:0 2px 0 0}.WB_expand .WB_func .WB_from{margin-bottom:0}.WB_feed_handle .WB_handle{overflow:hidden}.WB_feed_handle .WB_row_line{border-top-width:1px;border-top-style:solid}.S_line2{border-color:#f2f2f5}.WB_row_line{margin:0 0 0 -1px;zoom:1}.WB_feed_handle .WB_row_line{border-top-width:1px;border-top-style:solid}.S_line2{border-color:#f2f2f5}.WB_row_line{margin:0 0 0 -1px;zoom:1}.WB_row_r4 li{width:25%}.WB_row_line li{float:left;height:38px}</style>'

model0 = '<!DOCTYPE html><html lang="en" xmlns="http://www.w3.org/1999/html" xmlns="http://www.w3.org/1999/html"><head><meta charset="UTF-8">' \
    # 放羊式
model1 = '<title>微博内容</title></head><body><div class="weibo_box" style="width: 800px;background-color:whitesmoke;position: relative;"><div class="head" style="float: left;background-color: #329a86;position:relative;width: 100%;border-radius:25% 25% 0 0;"><div class="face" style="text-align: center;position: relative;top: 10px;">'
# 头像
model2 = '</div>'
# 昵称
# 时间
# 内容
model3 = '</div><div class="pictrue" style="float: left;">'
# 图片
model4 = '<div style="clear:both;"></div>' \
         '</div>' \
         '<div class="forwardweibo">' \
         '<div style="clear: both"></div>' \
         '<div class="forward_nick" style="color: #b0bdd0;font-weight: 500;' \
         'width:800px;margin: 0 auto;text-align: center;background-color:grey;">'
# 转发昵称
model5 = '</div>'
# 转发内容
model6 = '<div class="forward_pic">'
# 转发图片
model7 = '<div style="clear:both;"></div>' \
         '</div>' \
         '</div>' \
         '<div class="operation" style="margin-top:10px;text-align:center;">'
# 转发，评论，点赞数
model8 = '</div>' \
         '</div>' \
         '</body>' \
         '</html>'
style2 = "<style>div{margin:0;padding:0}ul{list-style:none;width:800px;text-align:center;margin:0 auto;padding:0;background-color:#deb887}a{text-decoration:none}.W_icon_tag_v2{display:none}</style>"


def cycleDo(fun, id, ti=60):
    logging.info("执行一次查询")
    fun(id)
    t = Timer(60 * int(ti), cycleDo, args=[fun, id, ti])
    t.start()


# 微博信息封装
class WeiBoMes():
    def __init__(self, nick, face, time, text, forwordnum, comment, praise, picture=None, sourcetext=None,
                 sourcenick=None):
        self.nick = str(nick)
        self.face = str(face)
        self.time = str(time)
        self.text = str(text)
        self.picture = str(picture)
        self.forwordnum = str(forwordnum)
        self.comment = str(comment)
        self.praise = str(praise)
        self.sourcetext = str(sourcetext)
        self.sourcenick = str(sourcenick)


class WeiBoMesManger(object):
    """ 
    - src_addr:   发送方的smtp服务器地址
    - des_mail:   目标邮箱地址
    - post:       stmp服务器端口
    - username    邮箱登录名
    - password    邮箱密码
    - mes         发送的信息
    - weiboID     要订阅的微博ID,为一个元组
    """

    def __init__(self, src_addr, port, des_mail, username, password, mes, *weiboID):
        self.src_addr = src_addr
        self.des_mail = des_mail
        self.port = port
        self.username = username
        self.password = password
        self.mes = mes
        self.weiboID = weiboID
        self.weibonum = None

    '''获取订阅微博的最新状态
        直接获取相应的Html文本，加上一点从微博提炼出的样式
        在移动端的邮箱上邮件渲染的不是很好看
        推荐使用getNewNes2()方法
    '''

    def getNewMes(self, weiboID):
        resp = self.passMes("http://weibo.com/u/" + weiboID)
        soup = BeautifulSoup(resp.text, "html.parser")
        weibonum = int(soup.find_all("strong", class_="W_f18")[2].contents[0])
        print(weibonum)

        if self.weibonum != None and self.weibonum != weibonum:
            blocks = soup.find_all("div", class_="WB_cardwrap WB_feed_type S_bg2 ")
            for num in range(weibonum - self.weibonum):
                self.sendMail(self.buildHtml(blocks[num]))
                # print(blocks[num])
        self.weibonum = int(weibonum)

    '''
    爬取微博有用的信息，用自己的样式渲染
    '''

    def getNewMes2(self, weiboID):
        # t1 = time.time()
        import gc
        weibonum=None
        try:
            resp = self.passMes("http://weibo.com/u/" + weiboID)
            print(resp.text)
            soup = BeautifulSoup(resp.text, "html.parser")
            '''正则匹配 已废弃 改用BeautifulSoup    
            #matches = re.findall(r'(?<=W_f18\">)\d+(?=<\/strong>)', resp.text) 
            #weibonum = matches[2]
            # timematchs=re.findall(r'(?<=:fromprofile\\">).+?(?=<\\/a>)',resp.text) #抓取时间
            # textmatches=re.findall(r'(?<=nick-name=\\"(.?)\\">).+?(?=<\\/div>)',resp.text) #抓取内容
            '''
            weibonum = int(soup.find_all("strong", class_="W_f18")[2].contents[0])
            """"细分为时间，文本和多媒体文件
            移动端的邮箱渲染功能只对元素的style属性识别
            所以就将样式天极爱进去，看着很乱
            """
            if self.weibonum != None and self.weibonum < weibonum:
                weibos = soup.find_all("div", class_="WB_cardwrap WB_feed_type S_bg2 ",
                                   limit=weibonum - self.weibonum)  # 获取新增的微博
                nick = soup.find("div", class_="pf_username")  # 获取昵称
                nick["style"] = "text-align: center;position: relative;margin-top: 5px;font-weight: 700;"
                nick.find("h1", class_="username")["style"] = "margin:0"
                face = soup.find("img", class_="photo")  # 获取头像
                face["style"] = "width: auto;width:100px;height: 100px;border-radius: 50%;"
                for num in range(weibonum - self.weibonum):
                    mid = weibos[num]["mid"]
                    gettime = weibos[num].find("div", attrs={"class": "WB_from S_txt2"})  # 获取时间
                    gettime[
                        "style"] = "text-align: center;position: relative;margin-top: 5px;font-size: 13px;color: #38547b;"
                    for a in gettime.find_all("a", class_="S_txt2"):
                        a["style"] = "font-size: 13px;color: #38547b;text-decoration:none"
                    text = weibos[num].find("div", attrs={"node-type": "feed_list_content"})  # 获取文本
                    text = self.extext(text, mid)
                    text["style"] = "text-align: center;position: relative;margin-top: 5px;font-size: 16px;color: " \
                                "#b0bdd0;width: 350px;margin: 10px auto;text-align: inherit;"
                    picture = weibos[num].find("ul", class_="WB_media_a")  # 获取多媒体文件
                    # 循环添加样式
                    if picture:
                        picture["style"] = "list-style: none;width: 800px;text-align: center;margin: 0 auto;" \
                                       "padding: 0;background-color:#deb887;"
                        newdiv = soup.new_tag("div", style="clear:both;")
                        picture.append(newdiv)
                        lis = picture.find_all("li", class_="WB_pic")
                        for li in lis:
                            li["style"] = "float: left;margin: 17px 0 0 87px;display: list-item;"
                            if li.i:
                                li.i["style"] = "display: none;"
                    # 是否为转发 逻辑异常捕捉
                    try:
                        weibos[num]["isforward"]  # 试错
                        omid = weibos[num]["omid"]
                        forwordnum = weibos[num].find_all("em", class_="W_ficon ficon_forward S_ficon")[
                                1].next_sibling  # 转发
                        forwordnum["style"] = "margin:0 75px;font-size: 15px;color: #38547b;"
                        comment = weibos[num].find_all("em", class_="W_ficon ficon_repeat S_ficon")[1].next_sibling  # 评论
                        comment["style"] = "margin:0 75px;font-size: 15px;color: #38547b;"
                        praise = weibos[num].find_all("em", class_="W_ficon ficon_praised S_txt2")[1].next_sibling  # 点赞
                        praise["style"] = "margin:0 75px;font-size: 15px;color: #38547b;"
                        sourcetext = weibos[num].find("div", attrs={"node-type": "feed_list_reason"})  # 原微博文本
                        sourcetext = self.extext(sourcetext, omid)
                        sourcetext[
                            "style"] = "background-color: #a2d3ef;padding: 10px 210px;text-align: center;position: relative;" \
                                    "font-size: 16px;color: " \
                                    "#4f5152;;width: 380px;margin: 0px auto;text-align: inherit;"
                        sourcenick = weibos[num].find("a", attrs={"node-type": "feed_list_originNick"})  # 原微博昵称
                        sourcenick["style"] = "color:#b0bdd0;text-decoration:none"
                        mesOT = WeiBoMes(nick, face, gettime, text, forwordnum, comment, praise, picture=picture,
                                        sourcetext=sourcetext, sourcenick=sourcenick)
                    except:
                        forwordnum = weibos[num].find_all("em", class_="W_ficon ficon_forward S_ficon")[
                            0].next_sibling  # 转发
                        forwordnum["style"] = "margin:0 75px;font-size: 15px;color: #38547b;"
                        comment = weibos[num].find_all("em", class_="W_ficon ficon_repeat S_ficon")[0].next_sibling  # 评论
                        comment["style"] = "margin:0 75px;font-size: 15px;color: #38547b;"
                        praise = weibos[num].find_all("em", class_="W_ficon ficon_praised S_txt2")[0].next_sibling  # 点赞
                        praise["style"] = "margin:0 75px;font-size: 15px;color: #38547b;"
                        mesOT = WeiBoMes(nick, face, gettime, text, forwordnum, comment, praise, picture=picture)
                    self.sendMail(self.buildHtml2(mesOT))
                    logging.info("发送一封邮件！")
        except Exception as e:
            logging.error("getNewMes2()--"+str(e))
        #print(weibonum)
        self.weibonum = (weibonum if weibonum is not None else self.weibonum)
        # print("getNewMes2()执行时间%s" %str(time.time()-t1))
        del resp, soup
        gc.collect()

    @staticmethod
    def passMes(url, params=None):
        # t1=time.time()
        # 伪装成搜索引擎爬虫  Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)
        # Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36
        headers = {"User-Agent":
                       "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
                   }
        try:
            resp = requests.get(url, params=params, headers=headers)
        except Exception as e:
            # try again
            logging.error("passMespassMes()--"+str(e))
            return None
        # print("passMes()执行时间%s" % str(time.time()-t1))
        return resp

    # 判断微博文本是否有隐藏文字
    def extext(self, mother, mid):
        # 判断是否有隐藏文字
        ex = mother.find("a", class_="WB_text_opt")
        if ex:
            resp = self.passMes("http://weibo.com/p/aj/mblog/getlongtext", params={"mid": mid})
            fulltext = BeautifulSoup(resp.json()['data']['html'], "html.parser")
            # print("html是%s" % str(fulltext))
            mother.clear()  # 移除text节点内的所有文本
            mother.append(fulltext)  # 将完整的文本嵌入
        return mother

    # @staticmethod
    def sendMail(self, Mes=None):
        ret = True
        try:
            msg = MIMEText(Mes, 'html', 'utf-8')  # 发送HTML文本
            msg['From'] = formataddr(["微博管理机器人", self.username])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To'] = formataddr(["订阅人", self.des_mail])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = "你订阅的人有微博更新啦！"  # 邮件的主题，也可以说是标题
            # print("Hello")
            server = smtplib.SMTP_SSL(self.src_addr, port=465)  # 发件人邮箱中的SMTP服务器，端口是25(默认)
            # server.set_debuglevel(1)
            server.login(self.username, self.password)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.username, [self.des_mail], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接
        except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False   hwbasymeslimbfie
            ret = False
            logging.error("sendMail come up error!")
        return ret

    """构建一个好看有用的Html页面"""

    def buildHtml(self, Block):
        # CSS代码植入
        return str(Block) + style

    """用自己的样式
       构建一个好看有用的Html页面
    """

    def buildHtml2(self, Mes):
        # mesOT = WeiBoMes(nick, face, time, text, picture, forwordnum, comment, praise, sourcetext, sourcenick)
        if Mes.sourcetext != "None":
            html = model0 + style2 + model1 + Mes.face + model2 + Mes.nick + Mes.time \
                   + Mes.text + model3 + model4 + Mes.sourcenick \
                   + model5 + Mes.sourcetext + model6 + (Mes.picture if Mes.picture != "None" else "") \
                   + model7 + Mes.forwordnum + "|" + Mes.comment + "|" + Mes.praise + model8
        else:
            html = model0 + style2 + model1 + Mes.face + model2 + Mes.nick + Mes.time \
                   + Mes.text + model3 + (Mes.picture if Mes.picture != "None" else "") + model4 \
                   + model5 + model6 \
                   + model7 + Mes.forwordnum + "|" + Mes.comment + "|" + Mes.praise + model8
        #print(html)
        return html


if __name__ == '__main__':
    import argparse
    import logging

    # 配置日志输出
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='weibo.log',
                        filemode='a')

    # 参数格式化提示
    parse = argparse.ArgumentParser(description='用于订阅指定微博用户的微博状态,'
                                                '如有微博更新，向指定邮箱发送一封邮件')
    parse.add_argument("-s", "--src_addr", default="smtp.qq.com",
                       help="发送方的smtp服务器地址")
    parse.add_argument("-d", "--des_mail", default="",
                       help="目标邮箱地址")
    parse.add_argument("-po", "--port", default="465",
                       help="stmp服务器端口")
    parse.add_argument("-u", "--username", default="",
                       help="邮箱登录名")
    parse.add_argument("-pass", "--password", default="",
                       help="邮箱密码")
    parse.add_argument("-m", "--mes", default="有更新!",
                       help="发送的信息")
    parse.add_argument("-id", "--weiboid", default="",
                       help="要订阅的微博ID")
    parse.add_argument("-t", "--time", default="60",
                       help="请求间隔时间")
    args = parse.parse_args()
    if args.src_addr and args.des_mail and args.port and args.username and args.password and args.mes:
        src_addr = args.src_addr
        des_mail = args.des_mail
        port = args.port
        username = args.username
        password = args.password
        mes = args.mes
        weiboID = args.weiboid
        ti = args.time
        print("ti %s" %ti)
    else:
        print("请正确输入参数！")
    manger = WeiBoMesManger(src_addr, port, des_mail, username, password, mes)
    cycleDo(manger.getNewMes2, weiboID, ti=1)
