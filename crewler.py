#import 函示庫
import requests
import pandas as pd
import io
import re
import time
import datetime
import pandas as pd
import sqlite3
import glob

#爬蟲,輸入日期格式為:20201109
def crawler(date_time):
    page_url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + date_time +'&type=ALLBUT0999'
    page = requests.get(page_url)
    use_text = page.text.splitlines()
    for i,text in enumerate(use_text):
        if text == '"證券代號","證券名稱","成交股數","成交筆數","成交金額","開盤價","最高價","最低價","收盤價","漲跌(+/-)","漲跌價差","最後揭示買價","最後揭示買量","最後揭示賣價","最後揭示賣量","本益比",':
            initial_point = i
            break
    test_df = pd.read_csv(io.StringIO(''.join([text[:-1] + '\n' for text in use_text[initial_point:]])))
    test_df['證券代號'] = test_df['證券代號'].apply(lambda x: x.replace('"',''))
    test_df['證券代號'] = test_df['證券代號'].apply(lambda x: x.replace('=',''))
    return test_df

#轉換日期格式為:yyyymmdd
def trans_date(date_time):
    return ''.join(str(date_time).split(' ')[0].split('-'))
#爬N天資料
def parse_n_days(start_date,n):
    df_dict = {}
    now_date = start_date
    for i in range(n):
        time.sleep(5)
        now_date = now_date - datetime.timedelta(days=1)
        try:
            df = crawler(trans_date(now_date))
            print("Current date" + trans_date(now_date))
            df_dict.update({trans_date(now_date):df})
            print('Successful!!')
        except:
            print('Fails at' + str(now_date))
    return df_dict

#範例,爬今天以前 5 天的資料,如果之前有資料庫這邊可以改1就會比較快
result_dict = parse_n_days(datetime.datetime.now(),30)

#將五天的資料存到csv裡面
for key in result_dict.keys():
    result_dict[key].to_csv(str(key)+'.csv')
######################################################
#從這裡開始將零散的CSV整理到資料庫中

#抓取所有的CSV檔案
All_csv_file = glob.glob('*.csv')
#創建資料庫,如果沒有會新建一個
dbname = 'TWStock.db'
db = sqlite3.connect(dbname)
#將All_csv_file丟到資料庫中
for file_name in All_csv_file:
    pd.read_csv(file_name).iloc[:,1:].to_sql(file_name.replace('.csv',''),db,if_exists='replace')

######################################################
#這裡開始將某一支股票過去幾天的資料單獨抓出來


#將csv的副檔名去掉,變成新的list
dates_list = [file_name.replace('.csv','') for file_name in All_csv_file]
#讀取剛剛匯入db中,所有日期的資料,重新放到新的DataFrame中
total_df = pd.DataFrame()
totalCnt = len(dates_list)
Cnt = 0
for date in dates_list: #這裡就是迴圈,一次讀取一個日期的資料,加到total資料表裡面
    df = pd.read_sql(con=db,sql='SELECT * FROM' + ' "'+ date +'"')#這句代表讀取sql裡面符合date的表格
    df['Date'] = date
    total_df = total_df.append(df)
    Cnt +=1
    print(str(Cnt)+'/'+str(totalCnt))
#創建個股資料表的資料庫以台積電(2330)為例子
dbname_Index = 'TWStock_ByIndex.db'
db_Index = sqlite3.connect(dbname_Index)
#將原本放到total_df內的資料根據證券代號分類,放到新的資料表中 
total_dict = dict(tuple(total_df.groupby('證券代號')))#這個分類可以自己調整,但要看一開始的csv有沒有這個分類
totalCnt = len(total_dict)
Cnt = 0
#這邊撈完以個股為表的資料庫就建立完成
for key in total_dict.keys():
    df = total_dict[key].iloc[:,2:]
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by=['Date'])
    df.to_sql(key,db_Index,if_exists='replace')
    Cnt +=1
    print('資料轉換中...'+str(Cnt)+'/'+str(totalCnt))

