from datetime import datetime
import pandas as pd
import pandas_datareader as pdr
import matplotlib.pyplot as plt
import sqlite3
import numpy as np
from matplotlib import dates as mdates
from matplotlib import ticker as mticker
from mpl_finance import candlestick_ohlc
from matplotlib.dates import DateFormatter
import datetime as dt

#連接資料庫
dbname_Index = 'TWStock_ByIndex.db'
db_Index = sqlite3.connect(dbname_Index)


#計算MA線
def moving_average(data,period):
    return data['Close'].rolling(period).mean()

#計算KD線
'''
Step1:計算RSV:(今日收盤價-最近9天的最低價)/(最近9天的最高價-最近9天的最低價)
Step2:計算K: K = 2/3 X (昨日K值) + 1/3 X (今日RSV)
Step3:計算D: D = 2/3 X (昨日D值) + 1/3 X (今日K值)
'''
def KD(data):
    data_df = data.copy()
    data_df['min'] = data_df['Low'].rolling(9).min()
    data_df['max'] = data_df['High'].rolling(9).max()
    data_df['RSV'] = (data_df['Close'] - data_df['min'])/(data_df['max'] - data_df['min'])
    data_df = data_df.dropna()
    # 計算K
    # K的初始值定為50
    K_list = [50]
    for num,rsv in enumerate(list(data_df['RSV'])):
        K_yestarday = K_list[num]
        K_today = 2/3 * K_yestarday + 1/3 * rsv
        K_list.append(K_today)
    data_df['K'] = K_list[1:]
    # 計算D
    # D的初始值定為50
    D_list = [50]
    for num,K in enumerate(list(data_df['K'])):
        D_yestarday = D_list[num]
        D_today = 2/3 * D_yestarday + 1/3 * K
        D_list.append(D_today)
    data_df['D'] = D_list[1:]
    use_df = pd.merge(data,data_df[['K','D']],left_index=True,right_index=True,how='left')
    print(use_df.tail())
    return use_df

def prepare_data(data):
    data_df = data.copy()
    data_df['Date'] = data_df.index
    #data_df = data_df.reset_index()
    data_df = data_df[['Date','Open','High','Low','Close','Volume']]
    data_df['Date'] = data_df.index.map(mdates.date2num)
    print(data_df)
    return data_df
    
# 畫股價圖
# 顏色:https://matplotlib.org/users/colors.html

#畫股價線圖與蠟燭圖
def plot_stock_price(data,df_KD,stockIndex):
    Ma_10 = moving_average(data,10)
    Ma_5 = moving_average(data,5)
    Length = len(data['Date'].values[60-1:])
    fig = plt.figure(facecolor='white',figsize=(15,10))
    ax1 = plt.subplot2grid((6,4), (0,0),rowspan=4, colspan=4, facecolor='w')
    candlestick_ohlc(ax1, data.values[-Length:],width=0.6,colorup='red',colordown='green')
    Label1 = '10 MA Line'
    Label2 = '5 MA Line'
    ax1.plot(data.Date.values[-Length:],Ma_10[-Length:],'black',label=Label1, linewidth=1.5)
    ax1.plot(data.Date.values[-Length:],Ma_5[-Length:],'navy',label=Label2, linewidth=1.5)
    ax1.legend(loc='upper center', ncol=2)
    ax1.grid(True, color='black')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.yaxis.label.set_color("black")
    plt.ylabel('Stock price and Volume')
    title = 'Stock Code:'+str(stockIndex)
    plt.suptitle(title,color='black',fontsize=16)
    #畫交易量
    ax1v = ax1.twinx()
    ax1v.fill_between(data.Date.values[-Length:],0, data.Volume.values[-Length:], facecolor='navy', alpha=.4)
    ax1v.axes.yaxis.set_ticklabels([])
    ax1v.grid(False)
    ax1v.set_ylim(0, 3*data.Volume.values.max())
    #加入KD線在下方
    #ax2 = plt.subplot2grid((6,4), (4,0), sharex=ax1, rowspan=1, colspan=4, facecolor='white')
    #ax2.plot(data.Date.values[-Length:], df_KD.K[-Length:],color='black')
    #ax2.plot(data.Date.values[-Length:], df_KD.D[-Length:],color='navy')
    #plt.ylabel('KD Value', color='black')


def drawStockPlot(stockname,stockIndex):
    stocks_dict = {}
    #將stockIndex放到 stockname 的 dict中
    stocks_dict.update({stockname:pd.read_sql(con=db_Index,sql='SELECT * FROM "'+str(stockIndex)+'"')})
    df_test = stocks_dict[stockname].copy()#複製一份到df_test進行操作
    df_test.index = pd.to_datetime(df_test['Date'])#index用日期排列
    df_test = df_test[['Date','開盤價','最高價','最低價','收盤價','成交股數']] #只留下這幾個欄位
    
    df_test['收盤價'] = df_test['收盤價'].apply(lambda x:x.replace(',',''))#去除逗號
    df_test['收盤價'] = pd.to_numeric(df_test['收盤價'])#將字串轉數字
    
    df_test['開盤價'] = df_test['開盤價'].apply(lambda x:x.replace(',',''))#去除逗號
    df_test['開盤價'] = pd.to_numeric(df_test['開盤價'])#將字串轉數字

    df_test['最高價'] = df_test['最高價'].apply(lambda x:x.replace(',',''))#去除逗號
    df_test['最高價'] = pd.to_numeric(df_test['最高價'])#將字串轉數字
    
    df_test['最低價'] = df_test['最低價'].apply(lambda x:x.replace(',',''))#去除逗號
    df_test['最低價'] = pd.to_numeric(df_test['最低價'])#將字串轉數字
   
    df_test['成交股數'] = df_test['成交股數'].apply(lambda x:x.replace(',',''))#去除逗號
    df_test['成交股數'] = pd.to_numeric(df_test['成交股數'])#將字串轉數字

    df_test.columns = ['Date','Open','High','Low','Close','Volume']#重新命名標頭
    #print(df_test.head())
    df_KD = KD(df_test)
    daysreshape = prepare_data(df_test)
    plot_stock_price(daysreshape,df_KD,stockIndex)
    plt.show()


#這邊可以選擇要畫出來的個股
#KD好像怪怪的
#drawStockPlot('創意',3443)
#drawStockPlot('台積電',2330)
drawStockPlot('微星',2377)

   
   