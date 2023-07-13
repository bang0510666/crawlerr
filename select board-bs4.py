import csv
import datetime
import requests
import bs4
import re
import time

def scrape_article(url):
    my_headers = {'cookie': 'over18=1;'}
    response = requests.get(url, headers=my_headers)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    header = soup.find_all('span', 'article-meta-value')
    if len(header) < 4:
        return None, None, None, None, None, None

    author = header[0].text
    board = header[1].text
    title = header[2].text

    # 獲取貼文內的時間信息
    date_str = header[3].text
    post_datetime = datetime.datetime.strptime(date_str, "%a %b %d %H:%M:%S %Y")
    date = post_datetime.strftime("%Y-%m-%d %H:%M:%S")

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
        comment = comment.replace(": ", "")
        comments.append(comment)

    return board, title, author, date, content, comments

def scrape_articles(board, target_year=None, target_date=None, timeout=300):
    if target_year is None:
        target_year = datetime.date.today().year
    if target_date is None:
        target_date = datetime.date.today()
    else:
        target_date = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
        target_date = target_date.replace(year=target_year)

    url = f"https://www.ptt.cc/bbs/{board}/index.html"
    my_headers = {'cookie': 'over18=1;'}
    count = 0
    page = 0
    filename = f"{board}_articles_{target_year}_{target_date}.csv"

    # 設置開始時間
    start_time = time.time()

    articles = []  # 儲存爬取到的文章

    while count < 100:
        response = requests.get(url, headers=my_headers)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        article_links = soup.select(".r-ent .title a")

        for link in article_links:
            if count >= 100:
                break

            article_url = "https://www.ptt.cc" + link["href"]
            board, title, author, date, content, comments = scrape_article(article_url)
            if board is None:
                continue

            post_datetime = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            if post_datetime.date() != target_date:
                continue

            articles.append([board, title, author, date, content, comments])
            count += 1

        page += 1
        next_link = soup.select_one(".btn-group-paging a:nth-child(2)")
        if next_link:
            url = "https://www.ptt.cc" + next_link["href"]
        else:
            break

        # 檢查是否超過設定時間
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time > timeout:
            break

    # 進行最終的篩選並將結果保存到CSV文件
    filtered_articles = [article for article in articles if datetime.datetime.strptime(article[3], "%Y-%m-%d %H:%M:%S").date() == target_date]
    with open(filename, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["看板", "標題", "作者", "發文時間", "內容", "留言"])
        writer.writerows(filtered_articles)

    print(f"爬取完成，结果已保存在{filename}中。")

# 示例：爬取指定年份和日期的最新100篇文章，如果超過10分鐘未找到數據則自動完成爬取
scrape_articles("Food", target_year=2023, target_date="2023-07-10", timeout=300)
