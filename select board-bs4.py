import csv
import datetime
import requests
import bs4
import re

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
        comment = comment.replace(": ", "")
        comments.append(comment)

    return board, title, author, date, content, comments

def scrape_articles(board, target_year=None, target_date=None):
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

    with open(filename, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["看板", "標題", "作者", "發文時間", "內容", "留言"])

        while count < 100:
            response = requests.get(url, headers=my_headers)
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            articles = soup.select(".r-ent")

            for article in articles:
                if count >= 100:
                    break

                title_element = article.select_one(".title a")
                if title_element is None:
                    continue

                title = title_element.text.strip()

                date_element = article.select_one(".meta .date")
                if date_element:
                    date_str = date_element.text.strip()
                    date = datetime.datetime.strptime(date_str, "%m/%d").date()
                    date = date.replace(year=target_year)
                else:
                    date = datetime.date.today()

                if date.year != target_year:
                    continue

                if date != target_date:
                    continue

                article_url = "https://www.ptt.cc" + title_element["href"]
                board, title, author, date, content, comments = scrape_article(article_url)
                if board is None:
                    continue

                writer.writerow([board, title, author, date, content, comments])
                count += 1

            page += 1
            next_link = soup.select_one(".btn-group-paging a:nth-child(2)")
            if next_link:
                url = "https://www.ptt.cc" + next_link["href"]
            else:
                break

    print(f"爬取完成，结果已保存在{filename}中。")


# 示例：爬取指定年份（2023）和日期（07-10）的最新100篇文章，如果没有指定日期则爬取当年当天的最新100篇内容
scrape_articles("Gossiping", target_year=2023, target_date="2023-07-10")
