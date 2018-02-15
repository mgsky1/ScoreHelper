import re
import urllib.request
import urllib.parse
import http.cookiejar
import bs4
from bs4 import BeautifulSoup

#准备Cookie和opener，因为cookie存于opener中，所以以下所有网页操作全部要基于同一个opener
cookie = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
#构造表单
params = {
    'txtUserName' : '学号',
    'Textbox1' : '',
    'Textbox2': '密码',
    'RadioButtonList1':'学生',
    'Button1' : '',
    'lbLanguage':'',
    'hidPdrs':'',
    'hidsc':'',
}

#获取ViewState
response = urllib.request.urlopen('http://218.5.241.21')
html = response.read().decode('gb2312')
viewstate = re.search('<input type="hidden" name="__VIEWSTATE" value="(.+?)"',html)
params['__VIEWSTATE'] = viewstate.group(1)

#获取验证码
res = opener.open('http://218.5.241.21/checkcode.aspx').read()
with open('code.jpg','wb') as file:
    file.write(res)
vcode = input('请输入验证码：')
params['txtSecretCode'] = vcode

#尝试登陆
loginurl = 'http://218.5.241.21/default2.aspx'
data = urllib.parse.urlencode(params).encode('gb2312')
response = opener.open(loginurl,data)

#构建查询全部成绩表单
params = {
    'ddlXN':'',
    'ddlXQ':'',
    'txtQSCJ':'0',
    'txtZZCJ':'100',
    'Button1':'在校学习成绩',
}

#构造Request对象，填入Header，防止302跳转，获取新的View_State
req = urllib.request.Request('http://218.5.241.21/xscj.aspx?xh=学号&xm=姓名(编码)&gnmkdm=N121604')
req.add_header('Referer','http://218.5.241.21/default2.aspx')
req.add_header('Origin','http://218.5.241.21')
response = opener.open(req)
html = response.read().decode('gb2312')
viewstate = re.search('<input type="hidden" name="__VIEWSTATE" value="(.+?)"',html)
params['__VIEWSTATE'] = viewstate.group(1)

#查询所有成绩
req = urllib.request.Request('http://218.5.241.21/xscj.aspx?xh=学号&xm=姓名(编码)&gnmkdm=N121604',urllib.parse.urlencode(params).encode('gb2312'))
req.add_header('Referer','http://218.5.241.21/default2.aspx')
req.add_header('Origin','http://218.5.241.21')
response = opener.open(req)
soup = BeautifulSoup(response.read().decode('gb2312'),'html.parser')
html = soup.find('table',class_='datelist')
print('你的所有成绩如下：')

#格式化宽度输出
mat = "{:^20}\t"

#根据DOM解析所要数据，首位的each是NavigatableString对象，其余为Tag对象
for each in html:
    if(type(each) == bs4.element.NavigableString):
        pass
    else:
        for item in each.contents:
            if(item != '\n'):
                print(mat.format(item.contents[0]),end='')
        print('\n')