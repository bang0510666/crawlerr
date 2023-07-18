import csv
import datetime
import requests
import bs4

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

    # 獲取貼文內的時間訊息
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

def scrape_articles(board, target_date=None):
    if target_date is None:
        target_date = datetime.date.today()

    url = f"https://www.ptt.cc/bbs/{board}/index.html"
    my_headers = {'cookie': 'over18=1;'}
    count = 0

    articles = []  # 儲存爬取到的文章

    while True:
        response = requests.get(url, headers=my_headers)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        article_links = soup.select(".r-ent .title a")

        # 判斷是否在時間範圍內
        first_article_url = "https://www.ptt.cc" + article_links[0]["href"]
        board, title, author, date, content, comments = scrape_article(first_article_url)
        if date is None:
            break

        post_datetime = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date()
        if post_datetime < target_date:
            # 爬取該頁的每篇文章
            for link in article_links:
                if count >= 100:
                    break

                article_url = "https://www.ptt.cc" + link["href"]
                board, title, author, date, content, comments = scrape_article(article_url)
                if board is None:
                    continue

                post_datetime = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date()
                if post_datetime >= target_date:
                    articles.append([board, title, author, date, content, comments])
                    count += 1

            break

        # 爬取該頁面的每一篇文章
        for link in article_links:
            if count >= 100:
                break

            article_url = "https://www.ptt.cc" + link["href"]
            board, title, author, date, content, comments = scrape_article(article_url)
            if board is None:
                continue

            articles.append([board, title, author, date, content, comments])
            count += 1

        prev_link = soup.select_one(".btn-group-paging a:nth-child(2)")
        if prev_link:
            url = "https://www.ptt.cc" + prev_link["href"]
        else:
            break

    # 過濾不符合指定日期範圍的文章
    filtered_articles = []
    for article in articles:
        post_datetime = datetime.datetime.strptime(article[3], "%Y-%m-%d %H:%M:%S").date()
        if post_datetime >= target_date:
            filtered_articles.append(article)

    # 按照發文時間進行排序
    sorted_articles = sorted(filtered_articles, key=lambda x: datetime.datetime.strptime(x[3], "%Y-%m-%d %H:%M:%S"), reverse=True)

    filename = f"{board}_articles_{target_date.strftime('%Y%m%d')}.csv"
    # 將结果保存到CSV文件
    with open(filename, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["看板", "標題", "作者", "發文時間", "內容", "留言"])
        writer.writerows(sorted_articles)

    print(f"爬取完成，结果已保存在{filename}中。")

# 示例：爬取從指定日期开始往過去的最新100篇文章
target_date = datetime.date(2023, 7, 15)
scrape_articles("Food", target_date)