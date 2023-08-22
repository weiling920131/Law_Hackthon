from django.shortcuts import render
from .models import dist, township
from .forms import locationForm
from .lasso import get_ratio, number_of_factor

import os
import requests
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta

# Calculator

def indexView(request):
    return render(request, 'calculator/index.html')

def resultView(request):
    m_name = request.POST.get('m_name')
    m_sum = int(request.POST.get('m_sum'))
    f_name = request.POST.get('f_name')
    f_sum = int(request.POST.get('f_sum'))
    ratio = float(request.POST.get('ratio'))

    toGive = m_name if m_sum >= f_sum else f_name
    toReceive = f_name if m_sum >= f_sum else m_name
    total = m_sum - f_sum if toGive == m_name  else f_sum - m_sum
    result = round(total / 2)
    special_result = round(total * (1 - ratio))

    return render(request, 'calculator/result.html', locals())

def result_m(request):
    male = {
        'name': request.POST.get('m_name', '您'),
        'deposit': int(request.POST.get('m_deposit', 0)),
        'insurance': int(request.POST.get('m_insurance', 0)),
        'stock': int(request.POST.get('m_stock', 0)),
        'house': int(request.POST.get('m_house', 0)),
        'property': int(request.POST.get('m_property', 0)),
        'fructus': int(request.POST.get('m_fructus', 0)),
        'credit': int(request.POST.get('m_credit', 0)),
        'loan': int(request.POST.get('m_loan', 0)),
    }
    if male['name'] == '':
        male['name'] = '您'
    m_sum = 0
    for k, v in male.items():
        if k =='name':
            continue
        elif k == 'credit' or k == 'loan':
            m_sum -= v
        else:
            m_sum += v

    score = []
    for i in range(number_of_factor):
        s = request.POST.get('score_' + str(i), 0)
        if s == '': 
            s = 0
        score.append(int(s))
    print(score)
    if score == [0] * number_of_factor:
        ratio = 0.0
    else:
        ratio = get_ratio(score)
    print('ratio', ratio)
    
    return render(request, 'calculator/result_m.html', locals())

def result_f(request):
    female = {
        'name': request.POST.get('f_name', '對方'),
        'deposit': int(request.POST.get('f_deposit', 0)),
        'insurance': int(request.POST.get('f_insurance', 0)),
        'stock': int(request.POST.get('f_stock', 0)),
        'house': int(request.POST.get('f_house', 0)),
        'property': int(request.POST.get('f_property', 0)),
        'fructus': int(request.POST.get('f_fructus', 0)),
        'credit': int(request.POST.get('f_credit', 0)),
        'loan': int(request.POST.get('f_loan', 0)),
    }
    if female['name'] == '':
        female['name'] = '對方'
    
    f_sum = 0
    for k, v in female.items():
        if k =='name':
            continue
        elif k == 'credit' or k == 'loan':
            f_sum -= v
        else:
            f_sum += v

    return render(request, 'calculator/result_f.html', locals())

def special_form(request):
    sf = request.GET.get('sf', 'close')
    return render(request, 'calculator/special_form.html', locals())

def special_score(request):
    checked = [ int(i) for i in request.POST.getlist('special')]
    all = []
    score = []
    for i in range(number_of_factor):
        all.append(i)
        s = request.POST.get('score_' + str(i), 0)
        if s == '': 
            s = 0
        score.append(int(s))
    # print(score)
    return render(request, 'calculator/special_score.html', locals())

# Stock

def crawl_price(index):
    date = datetime.now()
    if date.isoweekday() > 5:
        date -= timedelta(days = date.isoweekday() - 5)
    if date.hour < 15:
        date -= timedelta(days = 1)
        
    r = requests.get('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + str(date).replace('-','') + '&type=ALL')

    ret = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
                                        for i in r.text.split('\n') 
                                        if len(i.split('",')) == 17 and i[0] != '='])), header=0)
    ret = ret.set_index('證券代號')
    return ret.loc[index], date.date()

def search_stock(request):
    ss = request.GET.get('ss', 'close')
    return render(request, 'calculator/search/search_stock.html', locals())

def result_stock(request):
    index = request.POST.get('index', None)
    number = request.POST.get('number', None)

    res, date = crawl_price(index)
    
    context = {
        'name': res['證券名稱'],
        'price': res['收盤價'],
        'date': date,
        'total': float(res['收盤價']) * int(number),
    }
    return render(request, 'calculator/search/result_stock.html', context)

# Real Estate

def load(dist):
    path = 'calculator/data/real_estate'
    d = os.path.join(path, dist + '.csv')
    df = pd.read_csv(d, index_col=0)
    df.reset_index(drop=True, inplace=True)

    return df

def create_dist(request):
    dist.objects.all().delete()
    township.objects.all().delete()

    dist_township = [
        dist(dist_id='c', name='基隆市'),
        dist(dist_id='f', name='新北市'),
        dist(dist_id='a', name='臺北市'),
        dist(dist_id='h', name='桃園市'),
        dist(dist_id='j', name='新竹縣'),
        dist(dist_id='o', name='新竹市'),
        dist(dist_id='k', name='苗栗縣'),
        dist(dist_id='b', name='臺中市'),
        dist(dist_id='n', name='彰化縣'),
        dist(dist_id='m', name='南投縣'),
        dist(dist_id='p', name='雲林縣'),
        dist(dist_id='q', name='嘉義縣'),
        dist(dist_id='i', name='嘉義市'),
        dist(dist_id='d', name='臺南市'),
        dist(dist_id='e', name='高雄市'),
        dist(dist_id='t', name='屏東縣'),
        dist(dist_id='g', name='宜蘭縣'),
        dist(dist_id='u', name='花蓮縣'),
        dist(dist_id='v', name='臺東縣'),
        dist(dist_id='w', name='金門縣'),
        dist(dist_id='x', name='澎湖縣'),
        dist(dist_id='z', name='連江縣'),
    ]
    dist.objects.bulk_create(dist_township)

    for i in range(ord('a'), ord('z') + 1):
        d = chr(i)
        if(d == 'l' or d == 'r' or d == 's' or d == 'y'):
            continue
        df = load(d)
        town = set(df.loc[df['鄉鎮市區'].notnull(), '鄉鎮市區'])
        
        township.objects.bulk_create([township(dist_id=d, name=t) for t in town])
    
    return render(request, 'calculator/search/dist_list.html', {'d': dist.objects.all()})


def load_town(request):
    dist = request.GET.get('縣市')
    town_list = township.objects.filter(dist_id=dist)

    return render(request, 'calculator/search/dist_option.html', {'town_list': town_list})

    
def search_house(request):
    location = locationForm()
    sh = request.GET.get('sh', 'close')
    return render(request, 'calculator/search/search_house.html', locals())


def result_house(request):
    dist = request.GET.get('縣市')
    town = request.GET.get('鄉鎮市區')
    sign = request.GET.getlist('sign')
    address = str(request.GET.get('address'))
    build_type = request.GET.get('type')
    try: room = int(request.GET.get('room'))
    except: room = 0
    try: hall = int(request.GET.get('hall'))
    except: hall = 0
    try: bath = int(request.GET.get('bath'))
    except: bath = 0
    sort = request.GET.get('sort')

    df = load(dist)
    df['屋齡'] = datetime.now().year - 1911 - df['建築完成年'].astype(float)
    df['格局'] = df['房'].astype(str) + '房' + df['廳'].astype(str) + '廳' + df['衛'].astype(str) + '衛'
    row = (df['鄉鎮市區'] == town) & (df['交易標的'].isin(sign)) & (df['地址地號'].str.contains(address)) & (df['建物型態'].str.contains(build_type)) & (df['房'] >= room) & (df['廳'] >= hall) & (df['衛'] >= bath)
    col = ['地址地號', '交易日期', '單價元坪', '總面積坪', '交易標的', '屋齡', '建物型態', '格局', '車位類別']
    df = df.loc[row, col]
    df.fillna('--', inplace=True)

    if sort == 'time_latest':
        df.sort_values(['交易日期'], ascending=False, inplace=True)
    elif sort == 'time_oldest':
        df.sort_values(['交易日期'], ascending=True, inplace=True)
    elif sort == 'price_high':
        df.sort_values(['單價元坪'], ascending=False, inplace=True)
    elif sort == 'price_low':
        df.sort_values(['單價元坪'], ascending=True, inplace=True)
    elif sort == 'area_large':
        df.sort_values(['總面積坪'], ascending=False, inplace=True)
    elif sort == 'area_small':
        df.sort_values(['總面積坪'], ascending=True, inplace=True)
    
    price = df['單價元坪']
    count = len(price)
    try:
        avg_price = sum(price) / count / 10000
    except: 
        avg_price = 0.0

    df = df.iloc[:50]
    
    return render(request, 'calculator/search/result_house.html', locals())

