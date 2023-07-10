import csv
import datetime
import requests
from bs4 import BeautifulSoup

def scrape_hotboard():
    url = "https://www.ptt.cc/bbs/hotboards.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    board_elements = soup.select(".b-ent")
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"hotboards_{current_date}.csv"

    with open(filename, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["看板名稱", "熱門指數"])

        for board_element in board_elements:
            board_name = board_element.select_one(".board-name").text
            popularity = board_element.select_one(".board-nuser").text
            
            writer.writerow([board_name, popularity])
    
    print(f"熱門看板已爬取完成，結果已保存在{filename}中。")

# 爬取熱門看板並輸出為CSV檔案
scrape_hotboard()
