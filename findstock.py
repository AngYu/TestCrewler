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

dbname_Index = 'TWStock_ByIndex.db'
db_Index = sqlite3.connect(dbname_Index)

#這裡將2330的股票撈出n天來看,n是指從現在往前推n天
print(pd.read_sql(con=db_Index,sql='SELECT * FROM "2330"').tail())#tail 裡面的 1 就是 n 可以填要show幾天的

