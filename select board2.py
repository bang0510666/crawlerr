import csv
import datetime
import requests
import re
from bs4 import BeautifulSoup


def scrape_articles(board):
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
        writer = csv.writer(csvfile)
        writer.writerow(["標題", "發文時間", "作者", "內文", "留言"])

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

            author_element = article_soup.select_one("div.article-metaline:nth-child(1) span.article-meta-value")
            author = author_element.text.strip() if author_element else "N/A"

            content_element = article_soup.find(id="main-content")
            content = content_element.text.strip() if content_element else "N/A"
            content = re.sub(r"※ 發信站:.*", "", content)
            content = re.sub(r"※ 文章網址:.*", "", content)
            content = re.sub(r"※ 編輯:.*", "", content)
            content = re.sub(r'--\s*', '', content)
            content = content.replace(author, "").replace(post_time_str, "").replace(title, "")
            content = re.sub(r"\s+", " ", content)

            # 取得留言內容
            comments_elements = article_soup.select("div.push")
            comments = []
            for comment_element in comments_elements:
                comment_content = comment_element.select_one(".push-content").text.strip()
                comments.append(comment_content)

            # 写入CSV文件
            writer.writerow([title, post_time_str, author, content, "\n".join(comments)])

    print(f"爬取完成，结果已保存在{filename}中。")

scrape_articles("Gossiping")
