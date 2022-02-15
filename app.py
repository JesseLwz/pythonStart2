from tkinter.constants import END
from bs4 import BeautifulSoup
import requests
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.etree import cElementTree
import tkinter as tk

window = tk.Tk()
window.title('7MMTV爬蟲')
window.geometry('400x300')
window.configure(background='white')


def web_crawler():
    if(index_entry.get() != ''):
        goalSt = 'https://7mmtv.tv/zh/amateurjav_content/'+index_entry.get() + \
            '/index.html'
    else:
        key_word = num_entry.get()+"+7MMTV"
        html = requests.get('https://www.google.com/search',
                            headers={'Accept': 'application/json'},
                            # 搜尋 google.com/search?q={key_word}
                            params={'q': key_word}
                            )
        sp = BeautifulSoup(html.text, 'html.parser')
        # print(sp)
        st1 = sp.find("div", class_="kCrYT")
        # print(st1)
        st2 = st1.find("a").get("href")
        # print(st2)
        st3 = st2.replace('/url?q=', '').replace('/en/',
                                                 '/zh/').split("%5D%", 1)
        # 最終網址
        # print(st3[0]+"/index.html")
        goalSt = st3[0]+"/index.html"

    mmtv = requests.get(goalSt)
    mmtvsp = BeautifulSoup(mmtv.text, "html.parser")
    # print(mmtvsp)
    # 抓圖片網址與標題
    img = mmtvsp.find("div", class_="post-inner-details-img")
    if(img is None):
        result_label.configure(text=num_entry.get()+"找不到!")
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

window.mainloop()  # 在一般python xxx.py的執行方式中，呼叫mainloop()才算正式啟動
# 打包執行檔 pyinstaller -F -w -n justRunMe app.py
