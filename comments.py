import requests
import csv
import datetime
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
        writer.writerow(["標題", "內文", "留言"])

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

            # 提取內文元素
            content_element = article_soup.find(id="main-content")
            # 移除掉 metadata 和留言部分
            for elem in content_element.select('.article-metaline, .push'):
                elem.extract()
            content = content_element.get_text().strip()
            # 移除标题、看板名称以及相关HTML标签
            content = re.sub(re.escape(title), "", content)
            content = re.sub(r"\s*(<[^>]+>|※\s*(發信站|看板|文章網址|編輯):\s*.*|--.*)\s*", "", content)
            content = content.replace("看板 " + board, "")
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
            content = content.replace(title, "")
            lines = content.strip().splitlines()
            cleaned_content = " ".join(line for line in lines if line.strip())
            cleaned_content = re.sub(r'//.*', '', cleaned_content)
            # 提取留言部分
            
            #將原始碼做整理
            comments = []
            comment_elements = article_soup.find_all('div', class_='push')
            for comment_element in comment_elements:
                comment = comment_element.find('span', class_='push-content').text.strip()
                comments.append(comment)
           
            # 写入CSV文件
            writer.writerow([title, cleaned_content, comments])

    print(f"爬取完成，结果已保存在{filename}中。")
    

scrape_articles("Gossiping")
