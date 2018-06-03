'''
三明学院成绩查询助手V1.0
Coded By Martin Huang
2018.3.18
'''
import re
import urllib.request
import urllib.parse
import http.cookiejar
import bs4
import getpass
import pickle
import os
import platform
import subprocess
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from PIL import Image

#准备Cookie和opener，因为cookie存于opener中，所以以下所有网页操作全部要基于同一个opener
cookie = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))

#判断操作系统类型
def getOpeningSystem():
    return platform.system()

#判断是否联网

def isConnected():
    userOs = getOpeningSystem()
    if userOs == "Windows":
        subprocess.check_call(["ping", "-n", "2", "www.baidu.com"], stdout=subprocess.PIPE)
    else:
        subprocess.check_call(["ping", "-c", "2", "www.baidu.com"], stdout=subprocess.PIPE)

#登陆
def login():
    #构造表单
    params = {
        'txtUserName' : sid,
        'Textbox1' : '',
        'Textbox2': spwd,
        'RadioButtonList1':'学生',
        'Button1' : '',
        'lbLanguage':'',
        'hidPdrs':'',
        'hidsc':'',
    }
    #获取验证码
    res = opener.open('http://218.5.241.21/checkcode.aspx').read()
    with open(r'D:\Program Files\ScoreHelper\code.jpg','wb') as file:
        file.write(res)
    img = Image.open(r'D:\Program Files\ScoreHelper\code.jpg')
    img.show()
    vcode = input('请输入验证码：')
    img.close()
    params['txtSecretCode'] = vcode
    #获取ViewState
    response = urllib.request.urlopen('http://218.5.241.21')
    html = response.read().decode('gb2312')
    viewstate = re.search('<input type="hidden" name="__VIEWSTATE" value="(.+?)"',html)
    params['__VIEWSTATE'] = viewstate.group(1)
    #尝试登陆
    loginurl = 'http://218.5.241.21/default2.aspx'
    data = urllib.parse.urlencode(params).encode('gb2312')
    response = opener.open(loginurl,data)
    if response.geturl() == 'http://218.5.241.21/default2.aspx':
        print('登陆失败，可能是姓名、学号、密码、验证码填写错误！')
        return False
    else:
        return True

#获取成绩   
def getScore():
    #构造url
    url = ''.join([
            'http://218.5.241.21/xscj.aspx',
            '?xh=',
             sid,
            '&xm=',
            urllib.parse.quote(sname),
            '&gnmkdm=N121604',
        ])
    #构建查询全部成绩表单
    params = {
        'ddlXN':'',
        'ddlXQ':'',
        'txtQSCJ':'0',
        'txtZZCJ':'100',
        'Button1':'在校学习成绩',
    }
    #构造Request对象，填入Header，防止302跳转，获取新的View_State
    req = urllib.request.Request(url)
    req.add_header('Referer','http://218.5.241.21/default2.aspx')
    req.add_header('Origin','http://218.5.241.21')
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36')
    response = opener.open(req)
    html = response.read().decode('gb2312')
    viewstate = re.search('<input type="hidden" name="__VIEWSTATE" value="(.+?)"',html)
    params['__VIEWSTATE'] = viewstate.group(1)
    #查询所有成绩
    req = urllib.request.Request(url,urllib.parse.urlencode(params).encode('gb2312'))
    req.add_header('Referer','http://218.5.241.21/default2.aspx')
    req.add_header('Origin','http://218.5.241.21')
    response = opener.open(req)
    soup = BeautifulSoup(response.read().decode('gb2312'),'html.parser')
    html = soup.find('table',class_='datelist')
    print('你的所有成绩如下：')
    #指定要输出的列，原网页的表格列下标从0开始
    outColumn = [1,2,3,4,6,7,8]
    #用于标记是否是遍历第一行
    flag = True
    #根据DOM解析所要数据，首位的each是NavigatableString对象，其余为Tag对象
    #遍历行
    for each in html:
        columnCounter = 0
        column = []
        if(type(each) == bs4.element.NavigableString):
            pass
        else:
            #遍历列
            for item in each.contents:
                if(item != '\n'):
                    if columnCounter in outColumn:
                        #要使用str转换，不然陷入copy与deepcopy的无限递归
                        column.append(str(item.contents[0]).strip())
                    columnCounter += 1
            if flag:
                table = PrettyTable(column)
                flag = False
            else:
                table.add_row(column)
    print(table)

if __name__ == '__main__':
    try:
        print('欢迎使用三明学院成绩查询助手！')
        print('正在检查网络...')
        isConnected()
        with open(r'D:\Program Files\ScoreHelper\uinfo.bin','rb') as file:
            udick = pickle.load(file)
            sname = udick['sname']
            sid = udick['sid']
            spwd = udick['spwd']
        while(not login()):
            continue
        getScore()
    except FileNotFoundError:
        os.mkdir(r'D:\Program Files\ScoreHelper')#注：针对Windows目录结构
        print('这是你第一次使用，请按提示输入信息，以后可不必再次输入~')
        sid = input('请输入学号：')
        sname = input('请输入姓名：')
        #隐藏密码
        spwd = getpass.getpass('请输入密码：')
        while(not login()):
            sname = input('请输入姓名：')
            sid = input('请输入学号：')
            spwd = getpass.getpass('请输入密码：')
        getScore()
        udick = {'sname':sname,'sid':sid,'spwd':spwd}
        file = open(r'D:\Program Files\ScoreHelper\uinfo.bin','wb')
        pickle.dump(udick,file)
        file.close()
    except subprocess.CalledProcessError:
        print("网络连接不正常！请检查网络！")
    except:
        print("失败！可能是你没有完成教学评价！没有完成教学评价则无法查看成绩！")
    finally:
        input('Done！请按任意键退出')
