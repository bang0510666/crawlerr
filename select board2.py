import csv
import datetime
import requests
import re
from bs4 import BeautifulSoup


def scrape_articles(board, start_date=None, end_date=None):
    session = requests.Session()
    agree_url = "https://www.ptt.cc/ask/over18"
    session.post(agree_url, data={"from": "/bbs/" + board + "/index.html", "yes": "yes"})

    url = f"https://www.ptt.cc/bbs/{board}/index.html"
    response = session.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    article_elements = soup.select(".r-ent")
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{board}_articles_{current_date}.csv"

    with open(filename, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)  # 使用制表符作为分隔符
        writer.writerow(["標題", "發文時間", "作者", "內文", "留言內容"])

        for article_element in article_elements:
            title_element = article_element.select_one(".title")
            if not title_element:
                continue

            title = title_element.text.strip()
            link_element = title_element.select_one("a")
            if not link_element:
                continue

            link = link_element["href"]
            article_url = f"https://www.ptt.cc{link}"
            article_response = session.get(article_url)
            article_soup = BeautifulSoup(article_response.text, "html.parser")

            post_time_element = article_soup.select_one("div.article-metaline:nth-child(4) span.article-meta-value")
            post_time_str = post_time_element.text.strip() if post_time_element else "N/A"

            if post_time_str == "N/A":
                post_time = post_time_str
            else:
                # 转换日期字符串为datetime对象
                post_time = datetime.datetime.strptime(post_time_str, "%a %b %d %H:%M:%S %Y")

            author_element = article_soup.select_one("div.article-metaline:nth-child(1) span.article-meta-value")
            author = author_element.text.strip() if author_element else "N/A"

            content_element = article_soup.find(id="main-content")
            content = content_element.text.strip() if content_element else "N/A"
            # 精簡內容
            content = re.sub(r"作者.*", "", content)
            content = re.sub(r"看板.*", "", content)
            content = re.sub(r"標題.*", "", content)
            content = re.sub(r"時間.*", "", content)
            content = re.sub(r"https:.*", "", content)
            content = re.sub(r"※ 發信站:.*", "", content)
            content = re.sub(r"※ 文章網址:.*", "", content)
            content = re.sub(r"※ 編輯:.*", "", content)
            content = re.sub(r"--.*", "", content)
            content = content.replace(str(author), "").replace(str(post_time), "").replace(title, "")
            lines = content.strip().splitlines()
            cleaned_content = " ".join(line for line in lines if line.strip())
            cleaned_content = re.sub(r'//.*', '', cleaned_content)

            # 取得留言內容
            comments_elements = article_soup.select("div.push span.push-content")
            comments = [comment.text.strip() for comment in comments_elements]

            # 檢查是否有隱藏的留言
            hidden_comments_elements = article_soup.select("div.push span.push-content.hidden")
            for hidden_element in hidden_comments_elements:
                comments.append(hidden_element.text.strip())

            # 写入CSV文件
            writer.writerow([title, post_time_str, author, cleaned_content, "\n".join(comments)])

scrape_articles("Gossiping", start_date="2023-07-06", end_date="2023-07-07")
