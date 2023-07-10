# 引入所需函示庫
import csv
import datetime
import requests
import bs4
import re
# 定義scrape_article函數
def scrape_article(url):# 接收url
    my_headers = {'cookie': 'over18=1;'}
    response = requests.get(url, headers=my_headers)# 發送requests獲取頁面內容
    soup = bs4.BeautifulSoup(response.text, "html.parser")# 解析頁面

    header = soup.find_all('span', 'article-meta-value')
    author = header[0].text
    board = header[1].text
    title = header[2].text
    date = header[3].text

    main_container = soup.find(id='main-container')
    all_text = main_container.text
    pre_text = all_text.split('--')[0]
    texts = pre_text.split('\n')
    contents = texts[2:]
    content = '\n'.join(contents)

    comments = []
    push_elements = soup.select(".push")
    for push_element in push_elements:
        comment = push_element.select_one(".push-content").text.strip()
        comment=comment.replace(": ","")
        comments.append(comment)
    return board, title, author, date, content, comments
# 定義scrape_articles函數
def scrape_articles(board, target_date=None):# board表示要爬取的版面，target_date表示指定日期(默認為當天)
    if target_date is None:
        target_date = datetime.date.today()
    else:
        target_date = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()

    url = f"https://www.ptt.cc/bbs/{board}/index.html"
    my_headers = {'cookie': 'over18=1;'}
    count = 0
    page = 0
    filename = f"{board}_articles_{target_date}.csv"# 打開CSV文件，並使用"csv.writer"創建一個寫入器
    
    with open(filename, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["看板", "標題", "作者", "發文時間", "內容", "留言"])
        # 使用循環撥放，直到滿足100篇或沒有更多頁面
        while count < 100:
            response = requests.get(url, headers=my_headers)
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            articles = soup.select(".r-ent")

            for article in articles:
                if count >= 100:
                    break
                # 使用CSS選擇器逐一處理
                title_element = article.select_one(".title a")
                if title_element is None:
                    continue

                title = title_element.text.strip()
                # 檢查文章的日期是否滿足指定日期，若不滿足則跳過
                date_element = article.select_one(".meta .date")
                if date_element:
                    date_str = date_element.text.strip()
                    date = datetime.datetime.strptime(date_str, "%m/%d").date()
                    date = date.replace(year=target_date.year)
                else:
                    date = datetime.date.today()

                if date != target_date:
                    continue
                # 獲取文章連結，並調用"scrape_article"函數處理頁面
                article_url = "https://www.ptt.cc" + title_element["href"]
                board, title, author, date, content, comments = scrape_article(article_url)
                writer.writerow([board, title, author, date, content, comments])# 將提取的訊息寫入csv

                count += 1 #更新記數器

            page += 1 # 或取下一頁的連結
            next_link = soup.select_one(".btn-group-paging a:nth-child(2)")
            if next_link:
                url = "https://www.ptt.cc" + next_link["href"]
            else:
                break # 當循環結束，關閉CSV

    print(f"爬取完成，结果已保存在{filename}中。")


# 示例：爬取指定日期（2023-07-10）的最新100篇文章，如果没有指定日期則爬取當天的最新100篇内容
scrape_articles("Gossiping", target_date="2023-07-10")
