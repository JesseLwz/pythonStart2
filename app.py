from tkinter.constants import END
from bs4 import BeautifulSoup
import requests
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.etree import cElementTree
import tkinter as tk
from tkinter import ttk
import datetime
import windnd
# from tkinter.messagebox import  showinfo

window = tk.Tk()
window.title('7MMTV爬蟲')
window.geometry('400x300')
window.configure(background='white')


# 拖曳功能
def dragged_files(files):
    msg = '\n'.join((item.decode('gbk') for item in files))
    # showinfo('您拖放的文件',msg)
    batch_entry.delete(0,"end")
    batch_entry.insert(0, msg)

windnd.hook_dropfiles(window,func=dragged_files)


# 關鍵字或網址特定索引的爬蟲觸發入口
def web_crawler():
    if(index_entry.get() != ''):
        html = 'https://7mmtv.tv/zh/amateurjav_content/'+index_entry.get() + \
            '/index.html'
        searchName = index_entry.get()
    else:
        html = getKeyWordHtml(num_entry.get())
        searchName = num_entry.get() 
    # 呼叫爬蟲方法
    Scrapy(html,searchName)


# 藉由關鍵字取得google搜尋的網站網址
def getKeyWordHtml(key):  
        key_word = key+"+7MMTV"
        _html = requests.get('https://www.google.com/search',
                            headers={'Accept': 'application/json'},
                            # 搜尋 google.com/search?q={key_word}
                            params={'q': key_word}
                            )
        sp = BeautifulSoup(_html.text, 'html.parser')
        # print(sp)
        st1 = sp.find("div", class_="kCrYT")
        # print(st1)
        st2 = st1.find("a").get("href")
        # print(st2)
        st3 = st2.replace('/url?q=', '').replace('/en/',
                                                 '/zh/').split("%5D%", 1)
        # 最終網址
        # print(st3[0]+"/index.html")
        _html = st3[0]+"/index.html"  
        return _html


'''
爬蟲邏輯 
args1:網址
args2:關鍵字
'''
def Scrapy(goalSt, name):
    mmtv = requests.get(goalSt)
    mmtvsp = BeautifulSoup(mmtv.text, "html.parser")
    # print(mmtvsp)
    # 抓圖片網址與標題
    img = mmtvsp.find("div", class_="post-inner-details-img")
    if(img is None):
        result_label.configure(text=name+"找不到!")
        writeLog(name)
    else:
        imgTitle = img.find("img").get("title")
        imgSrc = img.find("img").get("src")
        # print(imgTitle)
        # print(imgSrc)
        # 抓資訊
        data = mmtvsp.find("span", class_="posts-inner-details-text-left")
        # # 番號
        num = data.select(".posts-message")[0].text.strip()
        # print(num)
        # # 發行日
        release = data.select(".posts-message")[1].text.strip()
        # print(release)
        # # 發行年
        if len(release) > 4:
            yesr = release[0:4]
        # # 片長 待補
        filename = num.split("-")[0]
        # print(filename)
        # 標籤
        tag = mmtvsp.find("span", class_="posts-inner-details-text-under")
        arTag = [t.text for t in tag.select("a")]
        # print(arTag)
        # 演員
        actor = mmtvsp.find("div", class_="actor-right-part")
        names = [t.text for t in actor.select("a") if t.text != ""]
        # print(names)
        saveDir = 'images/'+filename+'/'+num+'/'
        if not os.path.exists(saveDir):
            os.makedirs(saveDir)  # 遞迴建立資料夾
        img = requests.get(imgSrc)  # 下載圖片
        # 開啟資料夾及命名圖片檔 ex.images/300MIUM/300MIUM-322/300MIUM-322.jpg
        with open(saveDir + num + ".jpg", "wb") as file:
            file.write(img.content)  # 寫入圖片的二進位碼
        # 產出檔案
        filePath = saveDir + num + '.nfo'   # 指定檔名
        # 如果檔案已經存在，就停止執行
        if os.path.isfile(filePath):
            os.remove(filePath)   # 刪除檔案
        # 建立新的 XML 結構
        movie = ET.Element('movie')
        # 新增節點
        plot = ET.SubElement(movie, 'plot')
        plot.text = imgTitle
        title = ET.SubElement(movie, 'title')
        title.text = num
        # 新增actor節點
        for n in names:
            actor = ET.SubElement(movie, 'actor')
            actor_1 = ET.SubElement(actor, 'name')
            actor_1.text = n
            actor_2 = ET.SubElement(actor, 'type')
            actor_2.text = 'Actor'
        eleYear = ET.SubElement(movie, 'year')
        eleYear.text = yesr
        # 新增tag節點
        for t in arTag:
            tag = ET.SubElement(movie, 'tag')
            tag.text = t
        child = ET.SubElement(movie, 'poster')
        child.text = num + ".jpg"  # s_img
        child = ET.SubElement(movie, 'thumb')
        child.text = num + ".jpg"  # L_img
        child = ET.SubElement(movie, 'fanart')
        child.text = num + ".jpg"  # img
        child = ET.SubElement(movie, 'num')
        child.text = num + ".jpg"  # img
        child = ET.SubElement(movie, 'release')
        child.text = release
        # print(ET.tostring(movie))
        tree = cElementTree.ElementTree(movie)
        # Since ElementTree write() has no pretty printing support, used minidom to beautify the xml.
        t = minidom.parseString(ET.tostring(movie)).toprettyxml()
        tree1 = ET.ElementTree(ET.fromstring(t))
        # 輸出 XML 資料
        tree1.write(filePath, encoding='utf-8', xml_declaration=True)
        # 清空
        index_entry.delete(0, END)


# 批次爬蟲觸發入口
def web_batchCrawler():
    if(batch_entry.get() != ''):
        path = batch_entry.get() #資料夾目錄 EX.D:/myPython/sample
        files= os.listdir(path) #得到資料夾下的所有檔名稱
        for file in files: #遍歷資料夾
            fi_d = os.path.join(path, file)
            if os.path.isdir(fi_d): #判斷是否是資料夾
                cfiles= os.listdir(fi_d)
                for f in cfiles: #遍歷子資料夾
                    id = os.path.join(fi_d, f)
                    if os.path.splitext(id)[1]=='.mp4':
                        # print(file+'這是要執行的地方') #列印結果
                        # 開始爬
                        Scrapy(getKeyWordHtml(file),file)
                        break    

# 寫入LOG紀錄
def writeLog(txt):
    pathDir='logger'
    if not os.path.exists(pathDir):
        os.makedirs(pathDir)  # 遞迴建立資料夾
    # 有檔案寫入，無檔創建寫入
    file = open( pathDir+'/logger.txt', 'a', encoding = "utf-8" )
    file.write( txt+'未產生--'+str(datetime.datetime.now())+'\n')    
    file.close()


# 以下為 num 群組
num_frame = tk.Frame(window)
# 向上對齊父元件
num_frame.pack(side=tk.TOP)
num_label = tk.Label(num_frame, text='番號')
num_label.pack(side=tk.LEFT)
num_entry = tk.Entry(num_frame)
num_entry.pack(side=tk.LEFT)

# 以下為 7MMTV索引號 群組
index_frame = tk.Frame(window)
index_frame.pack(side=tk.TOP)
index_label = tk.Label(index_frame, text='索引')
index_label.pack(side=tk.LEFT)
index_entry = tk.Entry(index_frame)
index_entry.pack(side=tk.LEFT)

result_label = tk.Label(window)
result_label.pack()

calculate_btn = tk.Button(window, text='馬上爬蟲', command=web_crawler)
calculate_btn.pack()

# 分隔線
b=ttk.Separator(window,orient='horizontal')
b.pack(fill=tk.X)

# 資料夾批次搜尋
batch_frame = tk.Frame(window)
batch_frame.pack(padx=20, pady=10)
batch_label = tk.Label(batch_frame, text='資料夾目錄')
batch_label.pack(side=tk.LEFT)
batch_entry = tk.Entry(batch_frame)
batch_entry.pack(side=tk.LEFT)

batchScrapy_btn = tk.Button(window, text='批次爬蟲', command=web_batchCrawler)
batchScrapy_btn.pack()

window.mainloop()  # 在一般python xxx.py的執行方式中，呼叫mainloop()才算正式啟動
# 打包執行檔 pyinstaller -F -w -n justRunMe app.py
