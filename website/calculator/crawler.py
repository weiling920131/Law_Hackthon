import requests
import os
import zipfile
import time
import pandas as pd


pd.set_option('use_inf_as_na', True)

renameCol = {
    '土地位置建物門牌': '地址地號', '交易年月日': '交易日期', '建物現況格局-房': '房', '建物現況格局-廳': '廳', '建物現況格局-衛': '衛'
}

cols = [
    '縣市', '鄉鎮市區', '地址地號', '交易日期', '總價元', '單價元坪', '總面積坪', '交易標的', '建物型態', '建築完成年', '房', '廳', '衛', '車位類別'
]


def full2half(s):
    n = []
    for char in s:
        num = ord(char)
        if num == 0x3000:
            num = 32
        elif 0xFF01 <= num <= 0xFF5E:
            num -= 0xfee0
        num = chr(num)
        n.append(num)
    return ''.join(n)


def crawler(year, season):
    # make additional folder for files to extract
    folder = 'calculator/data/real_estate/raw/' + str(year) + str(season)
    if not os.path.isdir(folder):
        os.mkdir(folder)

        # download real estate zip content
        res = requests.get("https://plvr.land.moi.gov.tw//DownloadSeason?season="+str(year)+"S"+str(season)+"&type=zip&fileName=lvr_landcsv.zip")

        # save content to file
        fname = 'calculator/data/real_estate/raw/' + str(year) + str(season) + '.zip'
        open(fname, 'wb').write(res.content)

        # extract files to the folder
        with zipfile.ZipFile(fname, 'r') as zip_ref:
            zip_ref.extractall(folder)

        os.remove(fname)

        time.sleep(10)


def load(dist):
    print(dist)
    path = 'calculator/data/real_estate/raw'
    dirs = [d for d in os.listdir(path)]

    dfs = []
    dfs_build = []

    for d in dirs:
        d = os.path.join(path, d)
        
        d1 = os.path.join(d, dist + '_lvr_land_a.csv')
        df = pd.read_csv(d1)
        dfs.append(df.iloc[1:, :])
        try:
            d2 = os.path.join(d, dist + '_lvr_land_a_build.csv')
            df_build = pd.read_csv(d2)
            dfs_build.append(df_build.iloc[1:, :])
        except: pass

    df = pd.concat(dfs)
    try:
        df_build = pd.concat(dfs_build)

        df_build.drop_duplicates(subset=['編號'], inplace=True)
        df = pd.merge(df, df_build, how='left', on='編號')

        # 取得建築完成年分
        df['建築完成年'] = df['建築完成日期'].str.split('年').str[0]
    except: 
        df['建築完成年'] = None

    # 新增縣市代號
    df['縣市'] = dist
    df['土地位置建物門牌'] = [full2half(i) for i in df['土地位置建物門牌']]
    
    # 填入單價元平方公尺
    df['單價元平方公尺'] = df['單價元平方公尺'].astype(float)

    park = (df['單價元平方公尺'].isnull()) & (df['交易標的'] == '車位')
    df.loc[park, '單價元平方公尺'] = df.loc[park, '總價元'].astype(float) / df.loc[park, '車位移轉總面積平方公尺'].astype(float)

    land = (df['單價元平方公尺'].isnull()) & (df['交易標的'] == '土地')
    df.loc[land, '單價元平方公尺'] = df.loc[land, '總價元'].astype(float) / df.loc[land, '土地移轉總面積平方公尺'].astype(float)
    
    other = df['單價元平方公尺'].isnull()
    df.loc[other, '單價元平方公尺'] = df.loc[other, '總價元'].astype(float) / df.loc[other, '建物移轉總面積平方公尺'].astype(float)

    # 平方公尺換成坪
    df['單價元坪'] = df['單價元平方公尺'] * 3.3058
    df['總面積坪'] = df['總價元'].astype(float) / df['單價元坪'].astype(float)
    
    # 簡化建物型態
    df['建物型態'] = df['建物型態'].str.split('(').str[0]

    # 整理
    park = (df['交易標的'] == '車位')
    df.loc[park, '備註'] = ''
    dropRow = (df['單價元坪'].isnull()) | (df['總面積坪'].isnull()) | (df['備註'].str.contains('；'))
    df = df[~dropRow]
    df.rename(columns=renameCol, inplace=True)
    df = df[cols]
    df.reset_index(drop=True, inplace=True)
    
    # 存成csv檔
    df.to_csv('calculator/data/real_estate/' + dist + '.csv', encoding='utf_8_sig') 



# for y in range(110, 112):
#     for s in range(1, 5):
#         crawler(y, s)


for i in range(ord('a'), ord('z') + 1):
    dist = chr(i)
    if(dist == 'l' or dist == 'r' or dist == 's' or dist == 'y'):
        continue
    load(dist)