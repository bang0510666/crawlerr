# 載入selenium相關模組
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# 設定Chrome Driver 的執行檔路徑
options=Options()
options.chrome_executable_path="C:/Users/05731/OneDrive/桌面/crawler/chromedriver.exe"
# 建立Driver物件實體，用程式操作瀏覽器運作
driver=webdriver.Chrome(options=options)
driver.get("https://www.ptt.cc/bbs/Stock/index.html")
# print(driver.page_source) 取得網頁原始碼
tags=driver.find_elements(By.CLASS_NAME, "title")
for tag in tags:
    print(tag.text)
# 取得上一頁的文章標題
link=driver.find_element(By.LINK_TEXT, "‹ 上頁")
link.click() # 模擬使用者點擊連結標籤
tags=driver.find_elements(By.CLASS_NAME, "title")
for tag in tags:
    print(tag.text)
driver.close()