# Njupt_AutoJudge_requests

🔨   分分钟解决测评 

▲.需要Python环境

#### 安装依赖库

```
$ pip3 install -r requirements.txt
```

#### 如何使用

```
$ python app.py
```

接着，输入正方账号、密码即可



## 6.2 **记录几处改动**:

### 1.服务器上njupt模块版本为:

```
# 服务器
njupt               0.2.3 
# 我的windows上
njupt                 0.1.3
```

区别为:

- 0.2.3 使用`get_soup`
- 0.1.3使用`_url2soup`

### 2.增加了`gnmkdm`字段

### 3.增加考虑的JS大小写的情况(多于2名老师时)

### 4.`http://jwxt.njupt.edu.cn/xs_jsmydpj.aspx?`修改为`http://jwxt.njupt.edu.cn/xsjxpj.aspx?`