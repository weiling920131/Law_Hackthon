import requests
from datetime import datetime, timedelta
import pandas as pd
from io import StringIO

def crawl_price(index):
    date = datetime.now()
    if date.isoweekday() > 5:
        date -= timedelta(days = date.isoweekday() - 5)
    if date.hour < 15:
        date -= timedelta(days = 1)
        
    r = requests.get('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + str(date).replace('-','') + '&type=ALL')

    ret = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
                                        for i in r.text.split('\n') 
                                        if len(i.split('",')) == 17])), header=0)

    ret.loc[ret['證券代號'].str.startswith('='), '證券代號'] = ret.loc[ret['證券代號'].str.startswith('='), '證券代號'].str.split('"').str[1]
    ret.replace('--', 0, inplace=True)

    ret = ret.set_index('證券代號')
    print(ret.loc[index])

# crawl_price(0050)
