#import 函示庫
import requests
import pandas as pd
import io
import re
import time
import datetime
import matplotlib.pyplot as plt
import sqlite3
import numpy as np
import glob

#連接資料庫
dbname_Index = 'TWStock_ByIndex.db'
db_Index = sqlite3.connect(dbname_Index)
#這裡將2330的股票撈出n天來看,n是指從現在往前推n天
#print(pd.read_sql(con=db_Index,sql='SELECT * FROM "2330"').tail(4))#tail 裡面的 1 就是 n 可以填要show幾天的


stocks_dict = {}
#將2330放到 tsmc 的 dict中
stocks_dict.update({'tsmc':pd.read_sql(con=db_Index,sql='SELECT * FROM "2330"')})

#這段是教學測試用,看怎麼把收盤價的格式做一個轉換
df_test = stocks_dict['tsmc'].copy()#複製一份到df_test進行操作
df_test.index = pd.to_datetime(df_test['Date'])#index用日期排列
df_test = df_test[['證券名稱','收盤價']] #只留下兩攔
df_test['收盤價'] = df_test['收盤價'].apply(lambda x:x.replace(',',''))#去除逗號
df_test['收盤價'] = pd.to_numeric(df_test['收盤價'])#將字串轉數字
df_test.columns = ['stock_code','close']#重新命名標頭
print(df_test.head())


#這段才是真正要轉換的,將stocks_dict內的資料換成只有名稱跟收盤價
'''
在畫圖之前，
我們先整理我們的資料，將每個股票整理成股票名稱與收盤價的表格形式，
其中，因為收盤價被存為字串形式，我們也必須轉為數值形式做進一個的運算
'''

stock_dict_copy = {}

for key in stocks_dict.keys():
    df_test = stocks_dict[key]
    df_test.index = pd.to_datetime(df_test['Date'])#index用日期排列
    df_test = df_test[['證券名稱','收盤價']]
    df_test['收盤價'] = pd.to_numeric(df_test['收盤價'].apply(lambda x:x.replace(',','')),errors='coerce')
    df_test.columns = ['stock_code','close']
    stocks_dict[key] = df_test
    print(stocks_dict[key].head())


## 圖像判斷法
#如果我們要用最簡單的方式來估計我們持有股票的風險度的話，應該就是去估計股票的波動程度了，
#而我們可以選擇用標準差這個最常見的方式來測量波動程度。但是問題是，
#如果昨天的股票的統計性質與明天的股票的統計性質相差很大的話，
#我們就很難相信我們用過去股價估計出來的波動程度可以有效的衡量明天股價的波動程度，
#也就是說，我們希望我們前後天的股價是獨立且有相似的分配的，
#我們這邊可以用很簡單的圖像方式來呈現前後天股價的關係。

#用TSMC做例子
df = stocks_dict['tsmc'].copy()
df_p = df['2018-01-01':].iloc[:-1,:]
df_a = df['2018-01-01':].iloc[1:,:]
plt.scatter(np.array(df_p['close']),np.array(df_a['close']))
plt.show()
plt.hist([np.array(df['2018-01-01':'2018-09-01']['close']),np.array(df['2018-09-01':]['close'])])


