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
        writer.writerow(["標題", "發文時間", "作者", "內文"])

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

            # 提取內文元素
            content_element = article_soup.find(id="main-content")
            # 移除掉 metadata 和留言部分
            for elem in content_element.select('.article-metaline, .push'):
                elem.extract()
            content = content_element.get_text().strip()
            # 移除标题、看板名称以及相关HTML标签
            content = re.sub(re.escape(title), "", content)
            content = re.sub(r"\s*(<[^>]+>|※\s*(發信站|看板|文章網址|編輯):\s*.*|--.*)\s*", "", content)
            content = content.replace("看板" + board, "")

            # 写入CSV文件
            writer.writerow([title, post_time_str, author, content])

    print(f"爬取完成，结果已保存在{filename}中。")

scrape_articles("Gossiping")
