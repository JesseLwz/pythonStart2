import tkinter as tk
import os

window = tk.Tk()
window.title('7MMTV爬蟲')
window.geometry('400x300')
window.configure(background='white')


def calculate_bmi_number():
    # test = num_entry.get()
    os.getcwd()
    result = '你的路徑為：'+os.path.abspath(os.getcwd())
    result_label.configure(text=result)
    saveDir = 'test/'
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)  # 遞迴建立資料夾
    path = 'output.txt'
    with open(saveDir+path, 'w') as f:
        f.write('apple\n')
        f.write('banana\n')
        f.write('lemon\n')
        f.write('tomato\n')


# 以下為 height_frame 群組
num_frame = tk.Frame(window)
# 向上對齊父元件
num_frame.pack(side=tk.TOP)
num_label = tk.Label(num_frame, text='番號')
num_label.pack(side=tk.LEFT)
num_entry = tk.Entry(num_frame)
num_entry.pack(side=tk.LEFT)

result_label = tk.Label(window)
result_label.pack()

calculate_btn = tk.Button(window, text='馬上TEST', command=calculate_bmi_number)
calculate_btn.pack()

window.mainloop()  # 在一般python xxx.py的執行方式中，呼叫mainloop()才算正式啟動
