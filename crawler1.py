# 載入selenium相關模組
import csv
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# 設定Chrome Driver 的執行檔路徑
def scrape_hotboard():
    options=Options()
    options.chrome_executable_path="C:/Users/05731/OneDrive/桌面/crawler/chromedriver.exe"
# 建立Driver物件實體，用程式操作瀏覽器運作
    driver=webdriver.Chrome(options=options)
    driver.get("https://www.ptt.cc/bbs/hotboards.html")
# 等待熱門看板元素加載
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".b-ent")))
# 取得熱門看板元素
    board_elements = driver.find_elements(By.CSS_SELECTOR, ".b-ent")
# 取得當前日期元素
    current_date = datetime.date.today().strftime("%Y-%m-%d")
# 設定CSV檔案名稱
    filename = f"hotboards_{current_date}.csv"
# 建立CSV檔案並寫入標題行
    with open(filename, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["看板名稱", "熱門指數"])
        # 寫入每個熱門看板的名稱和熱門指數
        for board_element in board_elements:
            board_name = board_element.find_element(By.CSS_SELECTOR, ".board-name").text
            popularity = board_element.find_element(By.CSS_SELECTOR, ".board-nuser").text
            
            writer.writerow([board_name, popularity])
    print(f"熱門看板已爬取完成，結果已保存在{filename}中。")
    driver.close()
# 爬取熱門看板並輸出為CSV檔案
scrape_hotboard()