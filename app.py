# -*- coding: utf-8 -*-
# @Time    : 2019/12/1 21:44
# @Author  : Mrli
# @FileName: test.py
# @Cnblogs ：https://nymrli.top/
import re
import random
import sys
from lxml import etree
from njupt import Zhengfang
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlencode
from config import *
from exceptions import NoinputException, CoursesException, TeachersException

# headers = dict([line.split(":",1) for line in raw_headers.split("\n") if line])


# 使用charles抓包
proxy = {
    'http': '127.0.0.1:8888'
}


class Course(Zhengfang):
    '''
    课程测评
    '''
    def __init__(self, *args, **kwargs):
        super(Course, self).__init__(*args, **kwargs)
        self.account = kwargs.get('account')
        self.gnmkdm = ''

    # @staticmethod
    # def getcourses(account, cookies):

    def getcourses(self, account):
        '''
        通过首页,获得所有课程ID
        :return:
        '''
        # 首页
        index_url = 'http://jwxt.njupt.edu.cn/xs_main.aspx?xh={account}'.format(account=account)
        # html = getattr(requests, 'get')(url=index_url, headers=headers, cookies=cookies)
        html = self.get(index_url)
        content = etree.HTML(html.content)
        coursesList = []

        for i, c in enumerate(content.xpath('//*[@id="headDiv"]/ul/li[4]/ul/li')):
            class_url_suffix = c.xpath('a/@href')[0]
            if i == 0:
                self.gnmkdm = parse_qs(class_url_suffix).get('gnmkdm')[0]
            # 课程编号
            course_id = parse_qs(class_url_suffix).get('xsjxpj.aspx?xkkh')[0]
            coursesList.append(course_id)
        return coursesList

    def getFirstVIEWSTATE(self, course_id):
        '''
        通过首页的VIEWSTATE,找到指定课程pjkc的__VIEWSTATE
        :param classID: 爬取到的第一个课程ID
        :return: 指定课程pjkc的__VIEWSTATE
        '''
        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            # 需要填充pjkc、__VIEWSTATE、Button1(保存、提交)、DataGrid1:_ctl7:JS1
            'pjxx': '',
            'Button1': '保  存',
        }
        target_url = 'http://jwxt.njupt.edu.cn/xsjxpj.aspx?xkkh={classID}&xh={account}&gnmkdm={gnmkdm}'. \
            format(classID=course_id, account=self.account, gnmkdm=self.gnmkdm )
        view = self._get_viewstate(target_url)
        # 获得classID提交需要的首页__VIEWSTATE
        data['__VIEWSTATE'] = view
        # 指定需要获取课程的__VIEWSTATE
        data['pjkc'] = course_id
        r = self.post(target_url, data=data)
        soup = BeautifulSoup(r.content, 'lxml')
        viewstate = soup.find('input', attrs={"name": "__VIEWSTATE"}).get("value")
        return viewstate

    def saveComment(self, course_id, data):
        '''
        编码数据,并保存
        :param classID: 需要评价的课程
        :param data: 未编码的数据
        :return:
        '''
        target_url = 'http://jwxt.njupt.edu.cn/xsjxpj.aspx?xkkh={classID}&xh={account}&gnmkdm={gnmkdm}'. \
            format(classID=course_id, account=self.account, gnmkdm=self.gnmkdm )
        data['Button1'] = '保  存'
        data_gb2312 = urlencode(data, encoding='gb2312')
        # html = self.post(target_url, data=data_gb2312, proxies=proxy, headers=headers)
        html = self.post(target_url, data=data_gb2312, headers=headers)
        if html.status_code == 200:
            print("成功提交")

    def commitComment(self, course_id, data):
        '''
        编码数据,并提交
        :param classID: 需要评价的课程
        :param data: 未编码的数据
        :return:
        '''
        target_url = 'http://jwxt.njupt.edu.cn/xsjxpj.aspx?xkkh={classID}&xh={account}&gnmkdm={gnmkdm}'. \
            format(classID=course_id, account=self.account, gnmkdm=self.gnmkdm )
        data['Button2'] = '提  交'
        data_gb2312 = urlencode(data, encoding='gb2312')
        # html = self.post(target_url, data=data_gb2312, proxies=proxy, headers=headers)
        html = self.post(target_url, data=data_gb2312, headers=headers)
        if html.status_code == 200:
            print("成功提交")

    def getInputnums(self, course_id):
        '''
        通过课程ID获得下面需要提交的选项, 返回一个dict
        :param course_id:
        :return:
        '''
        course_url = 'http://jwxt.njupt.edu.cn/xsjxpj.aspx?xkkh={classID}&xh={stuID}'. \
            format(classID=course_id, stuID=self.account)
        # 获取网页
        html = self.get_soup(course_url)
        # print(dir(self))
        # html = self._url2soup(course_url)
        option = html.find_all('select', attrs={'name': re.compile('DataGrid1:_ctl\d+:[Jj][Ss]\d+')})
        if option:
            # 获得最后一个选项的id内容
            title = option[-1].get('name')
            # 处理选项信息
            lastinput = re.search('DataGrid1:_ctl(\d+):[Jj][Ss](\d+)', title)
            row, col = int(lastinput.group(1)), int(lastinput.group(2))
            data = {}
            if row and col:
                for c in range(1, col+1): # 从1开始
                    # lie = re.search('DataGrid1:_ctl(\d+):([Jj][Ss])(\d+)', title)
                    lielast = html.find_all('select',
                                    attrs={'name': re.compile('DataGrid1:_ctl\d+:[Jj][Ss]{col}'.
                                                              format(col=c))})[-1].get('name')
                    lie = re.search('DataGrid1:_ctl\d+:([Jj][Ss])\d+', lielast)
                    for r in range(1, row+1): # 从2开始 --> 从1开始全部
                        # data['DataGrid1:_ctl{rank}:JS1'.format(rank=rank)] = map_dict.get('完全认同')
                        data['DataGrid1:_ctl{row}:{js}{col}'.format(row=r, col=c, js=lie.group(1))] = '完全认同'
                    # data['DataGrid1:_ctl{rank}:JS1'.format(rank=random.randint(2, biggest))] = map_dict.get('勉强认同')
                    # data['DataGrid1:_ctl{row}:JS{col}'.format(row=random.randint(2, row), col=c)] = '勉强认同'
                    data['DataGrid1:_ctl{row}:{js}{col}'.format(row=random.randint(2, row), col=c, js = lie.group(1))] = '勉强认同'
            else:
                raise Exception('选项获取失败')
            return data

    def run(self, courses: list):
        for n, c in enumerate(courses):
            base = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                # 需要填充pjkc、__VIEWSTATE、Button1(保存、提交)、DataGrid1:_ctl7:JS1
                'pjxx': '',
                # 'Button1': '保  存',
            }
            # 生成选项
            grids_data = self.getInputnums(c)
            # print(grids_data)
            # 找到该课程的__VIEWSTATE
            base['__VIEWSTATE'] = self.getFirstVIEWSTATE(c)
            # 指定课程
            base['pjkc'] = c
            # 提交选项-->使用不同函数决定保存还是提交
            # base['Button1'] = '保  存'
            # 合并数据
            postdata = dict(base, **grids_data)
            # print(postdata)
            self.saveComment(c, postdata)
            if n == len(courses)-1:
                self.commitComment(c, postdata)


class Teacher(Zhengfang):
    '''
    教师测评
    '''
    def __init__(self, *args, **kwargs):
        super(Teacher, self).__init__(*args, **kwargs)
        self.account = kwargs.get('account')
        self.gnmkdm = ''

    def getFirstVIEWSTATE(self, course_id):
        '''
        通过首页的VIEWSTATE,找到指定课程pjkc的__VIEWSTATE
        :param classID: 爬取到的第一个课程ID
        :return: 指定课程pjkc的__VIEWSTATE
        '''
        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            # 需要填充pjkc、__VIEWSTATE、Button1(保存、提交)、DataGrid1:_ctl7:JS1
            'pjxx': '',
            'Button1': '保  存',
        }
        target_url = 'http://jwxt.njupt.edu.cn/xsjxpj.aspx?xkkh={classID}&xh={account}&gnmkdm={gnmkdm}'. \
            format(classID=course_id, account=self.account, gnmkdm=self.gnmkdm )
        view = self._get_viewstate(target_url)
        # 获得classID提交需要的首页__VIEWSTATE
        data['__VIEWSTATE'] = view
        # 指定需要获取课程的__VIEWSTATE
        data['pjkc'] = course_id
        r = self.post(target_url, data=data)
        soup = BeautifulSoup(r.content, 'lxml')
        viewstate = soup.find('input', attrs={"name": "__VIEWSTATE"}).get("value")
        return viewstate

    def getInputnums(self, course_id):
        '''
        通过课程ID获得下面需要提交的选项, 返回一个dict
        :param course_id:
        :return:
        '''
        course_url = 'http://jwxt.njupt.edu.cn/xsjxpj.aspx?xkkh={classID}&xh={stuID}&gnmkdm={gnmkdm}'. \
            format(classID=course_id, stuID=self.account, gnmkdm=self.gnmkdm )
        # 获取网页
        html = self.get_soup(course_url)
        # html = self._url2soup(course_url)
        
        # 找到最后一个选项
        option = html.find_all('select', attrs={'name': re.compile('DataGrid1:_ctl\d+:[Jj][Ss]\d+')})
        if option:
            # 获得最后一个选项的id内容
            title = option[-1].get('name')
            # 处理选项信息
            lastinput = re.search('DataGrid1:_ctl(\d+):[Jj][Ss](\d+)', title)
            row, col = int(lastinput.group(1)), int(lastinput.group(2))
            data = {}
            if row and col:
                # r->c, 列的数量少
                for c in range(1, col + 1):  # 从1开始
                    lielast = html.find_all('select',
                                    attrs={'name': re.compile('DataGrid1:_ctl\d+:[Jj][Ss]{col}'.
                                                              format(col=c))})[-1].get('name')
                    lie = re.search('DataGrid1:_ctl\d+:([Jj][Ss])\d+', lielast)
                    for r in range(1, row + 1):  # 从2开始
                        # 多个确定该列js的样式
                        data['DataGrid1:_ctl{row}:{js}{col}'.format(row=r, col=c, js = lie.group(1))] = '好'
                        # data['DataGrid1:_ctl{row}:txtjs{col}'.format(row=r, col=c)] = ''
                        # 只有JS会有大小写, txtjs全是小写
                        data['DataGrid1:_ctl{row}:txtjs{col}'.format(row=r, col=c)] = ''
                    randOption = random.randint(1, row)
                    data['DataGrid1:_ctl{row}:{js}{col}'.format(row=randOption, col=c, js = lie.group(1))] = '较好'
            else:
                raise Exception('选项获取失败')
            return data


    def saveComment(self, course_id, data):
        '''
        编码数据,并保存
        :param classID: 需要评价的课程
        :param data: 未编码的数据
        :return:
        '''
        target_url = 'http://jwxt.njupt.edu.cn/xsjxpj.aspx?xkkh={classID}&xh={account}&gnmkdm={gnmkdm}'. \
            format(classID=course_id, account=self.account, gnmkdm=self.gnmkdm )
        data['Button1'] = '保  存'
        data['txt1'] = ''
        data['TextBox1'] = '0'
        data_gb2312 = urlencode(data, encoding='gb2312')
        # html = self.post(target_url, data=data_gb2312, proxies=proxy, headers=headers)
        html = self.post(target_url, data=data_gb2312, headers=headers)
        if html.status_code == 200:
            print("成功提交")

    def commitComment(self, course_id, data):
        '''
        编码数据,并提交
        :param classID: 需要评价的课程
        :param data: 未编码的数据
        :return:
        '''
        target_url = 'http://jwxt.njupt.edu.cn/xsjxpj.aspx?xkkh={classID}&xh={account}&gnmkdm={gnmkdm}'. \
            format(classID=course_id, account=self.account, gnmkdm=self.gnmkdm )
        data['Button2'] = '提  交'
        data['txt1'] = ''
        data['TextBox1'] = '0'
        data_gb2312 = urlencode(data, encoding='gb2312')
        # html = self.post(target_url, data=data_gb2312, proxies=proxy, headers=headers)
        html = self.post(target_url, data=data_gb2312, headers=headers)
        if html.status_code == 200:
            print("成功提交")

    def run(self, courses: list):
        for n, c in enumerate(courses):
            base = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                # 需要填充pjkc、__VIEWSTATE、Button1(保存、提交)、DataGrid1:_ctl7:JS1
                'pjxx': '',
                # 'Button1': '保  存',
            }
            # 生成选项
            grids_data = self.getInputnums(c)
            # 找到该课程的__VIEWSTATE
            base['__VIEWSTATE'] = self.getFirstVIEWSTATE(c)
            # # 指定课程
            base['pjkc'] = c
            # # 合并数据
            postdata = dict(base, **grids_data)
            self.saveComment(c, postdata)
            if n == len(courses)-1:
                self.commitComment(c, postdata)


class AutoJudge():
    def __init__(self, account=None, password=None):
        if account and password:
            self.account = account
            self.c = Course(account=account, password=password)
            self.t = Teacher(account=account, password=password)
        else:
            raise NoinputException()
            # raise Exception("请输入账号密码")

    def run(self):
        # 获得该学期所有课程
        try:
            courses = self.c.getcourses(account=self.account)
        except Exception as e:
            print(e)
            return -1
        if courses:
            # 完成课程评价
            # print(courses)
            try:
                self.c.run(courses)
            except AttributeError as e:
                sys.stderr.write("CoursesException-AttributeError: 'NoneType' object has no attribute 'get'")
                raise CoursesException()
            else:
                print('---课程评价完成---')
            # 完成老师评价
            try:
                self.t.run(courses)
            except AttributeError as e:
                sys.stderr.write("TeachersException-AttributeError: 'NoneType' object has no attribute 'get'")
                raise TeachersException()
            else:
                print('---教师评价完成---')
            return 0
        else:
            print("接口未开放or已经全部测评完！")
            return -1


if __name__ == '__main__':
    account = input('请输入您的学号:')
    password = input('请输入正方的密码:')
    agent = AutoJudge(account=account, password=password)
    agent.run()
