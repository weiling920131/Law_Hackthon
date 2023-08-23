# Law_Hackthon
## 使用方法
### 1. 在Google Colab上執行
> 較簡單、省時，但操作網站時容易卡頓，沒反應時可多按幾下

**[https://colab.research.google.com/drive/16lVcmaFIyzqcldOwcKYXw4ARNZXBDRCA?usp=drive_link](https://colab.research.google.com/drive/16lVcmaFIyzqcldOwcKYXw4ARNZXBDRCA?usp=drive_link)**

#### 步驟：
1. 執行階段 -> 全部執行
2. 成功的話會看到類似以下內容

![image](https://github.com/weiling920131/Law_Hackthon/assets/86657062/5ca571f1-e755-4ec2-aee6-54bcff83bc71)

3. 點第三欄輸出的網址開啟網站

![image](https://github.com/weiling920131/Law_Hackthon/assets/86657062/01423d64-e0a0-499b-bae3-dd881605c715)

4. 完成:D

### 2. 在本機上執行
> 較麻煩，需要一段時間安裝，建議要有程式基礎，但操作網站很順暢
#### 建置Anaconda環境：
1. 安裝Anaconda
2. 在website資料夾中開啟終端機
3. 輸入 `conda env create -f environment.yml` 安裝環境

#### 執行程式：
1. 在website資料夾中開啟終端機
2. 輸入 `conda activate django` 進入安裝好的環境
3. 輸入 `python manage.py runserver`
4. 成功的話會看到類似以下內容

![image](https://github.com/weiling920131/Law_Hackthon/assets/86657062/446f6661-2cd6-4d0d-8ba8-db7b64e5f6d4)
 
5. 打開瀏覽器輸入網址 `localhost:8000`
6. 完成:D
